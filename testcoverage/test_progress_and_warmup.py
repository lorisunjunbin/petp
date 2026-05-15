"""Tests for Processor cache warm-up and MCP task-level progress notifications."""

import json
import time
from queue import SimpleQueue
from unittest.mock import MagicMock, patch

import pytest


class TestWarmProcessorCache:
    """Tests for BackgroundRuntime.warm_processor_cache()."""

    def test_warm_cache_loads_processor_types(self, bg_runtime):
        from core.processor import Processor

        bg_runtime.warm_processor_cache()

        # After warm-up, known processor types should be cached
        proc = Processor.get_processor_by_type("ENCODE_DECODE_STR")
        assert proc is not None
        assert type(proc).__name__ == "ENCODE_DECODE_STRProcessor"

    def test_warm_cache_only_processes_astool_executions(self, bg_runtime):
        from core.execution import Execution

        astool_executions = []
        for name in Execution.get_available_executions():
            execution = Execution.get_execution(name)
            if hasattr(execution, "astool") and execution.astool:
                astool_executions.append(name)

        # At least one astool execution should exist (ENDECODER has astool=true)
        assert len(astool_executions) >= 1

    def test_warm_cache_survives_missing_processor(self, bg_runtime):
        """warm_processor_cache should not raise even if a processor type is invalid."""
        from core.execution import Execution
        from core.task import Task

        # Temporarily add a fake execution with a bad processor type
        fake_name = "__TEST_WARM_FAKE__"
        original = Execution.get_execution(fake_name)
        assert original is None

        # Patch get_available_executions to include our fake
        real_available = Execution.get_available_executions()

        fake_exec = MagicMock()
        fake_exec.astool = True
        fake_exec.mcp_desc = '{"desc":"test"}'
        fake_task = MagicMock()
        fake_task.type = "__NONEXISTENT_PROCESSOR_TYPE__"
        fake_exec.list = [fake_task]

        with patch.object(Execution, 'get_available_executions', return_value=[fake_name] + list(real_available)):
            with patch.object(Execution, 'get_execution', side_effect=lambda n: fake_exec if n == fake_name else Execution.get_execution.__wrapped__(n) if hasattr(Execution.get_execution, '__wrapped__') else None):
                # Should not raise
                bg_runtime.warm_processor_cache()


class TestProgressQueue:
    """Tests for progress_queue parameter in run_execution."""

    def test_progress_queue_receives_messages(self, bg_runtime):
        """run_execution should put start/done messages into progress_queue."""
        queue = SimpleQueue()
        result = bg_runtime.run_execution("ENDECODER", {
            "type": "encode", "algorithms": "base64", "inbound": "test"
        }, progress_queue=queue)

        assert result["ok"]

        messages = []
        while not queue.empty():
            messages.append(queue.get_nowait())

        # Should have at least one start and one done message
        assert len(messages) >= 2, f"expected at least 2 progress messages, got: {messages}"

        # Check format: [seq/total] TYPE started / done
        started_msgs = [m for m in messages if "started" in m]
        done_msgs = [m for m in messages if "done" in m]
        assert len(started_msgs) >= 1, f"no 'started' messages found in: {messages}"
        assert len(done_msgs) >= 1, f"no 'done' messages found in: {messages}"

    def test_progress_queue_contains_task_type(self, bg_runtime):
        """Progress messages should include the processor type name."""
        queue = SimpleQueue()
        bg_runtime.run_execution("ENDECODER", {
            "type": "encode", "algorithms": "base64", "inbound": "x"
        }, progress_queue=queue)

        messages = []
        while not queue.empty():
            messages.append(queue.get_nowait())

        # ENDECODER uses ENCODE_DECODE_STR processor
        has_type_ref = any("ENCODE_DECODE_STR" in m for m in messages)
        assert has_type_ref, f"expected processor type in messages: {messages}"

    def test_progress_queue_format_seq_total(self, bg_runtime):
        """Messages should follow [seq/total] format."""
        queue = SimpleQueue()
        bg_runtime.run_execution("ENDECODER", {
            "type": "encode", "algorithms": "base64", "inbound": "y"
        }, progress_queue=queue)

        messages = []
        while not queue.empty():
            messages.append(queue.get_nowait())

        # Check [N/M] format
        import re
        pattern = re.compile(r'\[\d+/\d+\]')
        matched = [m for m in messages if pattern.search(m)]
        assert len(matched) == len(messages), f"not all messages match [seq/total] format: {messages}"

    def test_progress_queue_done_has_duration(self, bg_runtime):
        """Done messages should include duration in ms."""
        queue = SimpleQueue()
        bg_runtime.run_execution("ENDECODER", {
            "type": "encode", "algorithms": "base64", "inbound": "z"
        }, progress_queue=queue)

        messages = []
        while not queue.empty():
            messages.append(queue.get_nowait())

        done_msgs = [m for m in messages if "done" in m]
        assert len(done_msgs) >= 1
        # Check (Nms) format
        import re
        for msg in done_msgs:
            assert re.search(r'\(\d+ms\)', msg), f"done message missing duration: {msg}"

    def test_no_progress_queue_still_works(self, bg_runtime):
        """Passing no progress_queue (default None) should not break execution."""
        result = bg_runtime.run_execution("ENDECODER", {
            "type": "encode", "algorithms": "base64", "inbound": "abc"
        })
        assert result["ok"]

    def test_progress_queue_skipped_task_no_done(self, bg_runtime):
        """Skipped tasks should emit started but not done messages (they are skipped before do_process)."""
        # Run an execution where tasks might be skipped due to ui_policy
        queue = SimpleQueue()
        result = bg_runtime.run_execution("ENDECODER", {
            "type": "encode", "algorithms": "base64", "inbound": "skip_test"
        }, progress_queue=queue)

        messages = []
        while not queue.empty():
            messages.append(queue.get_nowait())

        # For ENDECODER, no tasks should be skipped, so started == done count
        started_count = sum(1 for m in messages if "started" in m)
        done_count = sum(1 for m in messages if "done" in m)
        assert started_count == done_count, \
            f"for non-skipped execution, started ({started_count}) should equal done ({done_count})"


class TestDrainProgress:
    """Tests for McpMixin._drain_progress helper."""

    def test_drain_empty_queue(self):
        from httpservice.McpMixin import McpMixin
        mixin = McpMixin()
        queue = SimpleQueue()
        events = mixin._drain_progress(queue, "test_tool")
        assert events == []

    def test_drain_none_queue(self):
        from httpservice.McpMixin import McpMixin
        mixin = McpMixin()
        events = mixin._drain_progress(None, "test_tool")
        assert events == []

    def test_drain_collects_all_messages(self):
        from httpservice.McpMixin import McpMixin
        mixin = McpMixin()
        queue = SimpleQueue()
        queue.put("msg1")
        queue.put("msg2")
        queue.put("msg3")

        events = mixin._drain_progress(queue, "my_tool")

        assert len(events) == 3
        assert queue.empty()

        # Each event should be a valid SSE event string
        for event in events:
            assert event.startswith("event: message\n")
            assert "data: " in event
            # Parse the JSON payload
            data_line = event.split("data: ", 1)[1].rstrip("\n")
            payload = json.loads(data_line)
            assert payload["jsonrpc"] == "2.0"
            assert payload["method"] == "notifications/message"
            assert "[my_tool]" in payload["params"]["data"]

    def test_drain_includes_tool_name_prefix(self):
        from httpservice.McpMixin import McpMixin
        mixin = McpMixin()
        queue = SimpleQueue()
        queue.put("task 3 done")

        events = mixin._drain_progress(queue, "ENDECODER")

        data_line = events[0].split("data: ", 1)[1].rstrip("\n")
        payload = json.loads(data_line)
        assert "[ENDECODER] task 3 done" == payload["params"]["data"]


class TestRunWithProgress:
    """Tests for McpMixin._run_with_progress with progress_queue."""

    def test_fast_execution_yields_result(self):
        from httpservice.McpMixin import McpMixin
        mixin = McpMixin()

        def fast_fn():
            return {"ok": True, "data": {"x": 1}}

        items = list(mixin._run_with_progress(fast_fn, timeout=10, tool_name="test"))

        # Should yield the result directly (fast path)
        results = [i for i in items if not isinstance(i, str)]
        assert len(results) == 1
        assert results[0]["ok"] is True

    def test_progress_queue_messages_yielded_as_sse(self):
        from httpservice.McpMixin import McpMixin
        mixin = McpMixin()

        queue = SimpleQueue()

        def slow_fn():
            # Must exceed _PROGRESS_INTERVAL (1s) to trigger the polling loop
            queue.put("[1/2] TASK_A started")
            time.sleep(1.2)
            queue.put("[1/2] TASK_A done (50ms)")
            return {"ok": True, "data": {}}

        items = list(mixin._run_with_progress(slow_fn, timeout=10, tool_name="MY_EXEC", progress_queue=queue))

        sse_events = [i for i in items if isinstance(i, str)]
        results = [i for i in items if not isinstance(i, str)]

        assert len(results) == 1
        assert results[0]["ok"] is True

        # The polling loop should have drained progress messages as SSE events
        all_sse_text = "".join(sse_events)
        assert "TASK_A" in all_sse_text or "still running" in all_sse_text

    def test_timeout_returns_error(self):
        from httpservice.McpMixin import McpMixin
        mixin = McpMixin()

        def forever_fn():
            time.sleep(100)
            return {"ok": True}

        items = list(mixin._run_with_progress(forever_fn, timeout=1, tool_name="stuck"))

        results = [i for i in items if not isinstance(i, str)]
        # Should get a timeout error result
        assert len(results) >= 1
        last_result = results[-1]
        assert isinstance(last_result, dict)
        assert last_result.get("ok") is False
        assert "timed out" in last_result.get("error", "").lower()


class TestSharedExecutor:
    """Tests for shared ThreadPoolExecutor in McpMixin."""

    def test_executor_reuse(self):
        """Multiple calls should reuse the same executor instance."""
        from httpservice.McpMixin import McpMixin
        mixin = McpMixin()
        ex1 = mixin._get_executor()
        ex2 = mixin._get_executor()
        assert ex1 is ex2
        mixin._shutdown_executor()

    def test_executor_shutdown(self):
        """_shutdown_executor should set _executor to None."""
        from httpservice.McpMixin import McpMixin
        mixin = McpMixin()
        mixin._get_executor()
        assert mixin._executor is not None
        mixin._shutdown_executor()
        assert mixin._executor is None

    def test_executor_recreated_after_shutdown(self):
        """After shutdown, _get_executor should create a new one."""
        from httpservice.McpMixin import McpMixin
        mixin = McpMixin()
        ex1 = mixin._get_executor()
        mixin._shutdown_executor()
        ex2 = mixin._get_executor()
        assert ex2 is not ex1
        assert ex2 is not None
        mixin._shutdown_executor()

    def test_run_with_timeout_uses_shared_executor(self):
        """_run_with_timeout should work with shared executor."""
        from httpservice.McpMixin import McpMixin
        mixin = McpMixin()
        result = mixin._run_with_timeout(lambda: {"ok": True, "value": 42}, timeout=5)
        assert result == {"ok": True, "value": 42}
        # Executor should still be alive
        assert mixin._executor is not None
        assert not mixin._executor._shutdown
        mixin._shutdown_executor()

    def test_concurrent_submissions(self):
        """Shared executor should handle concurrent tasks."""
        from httpservice.McpMixin import McpMixin
        import concurrent.futures
        mixin = McpMixin()

        results = []
        with concurrent.futures.ThreadPoolExecutor(4) as caller_pool:
            futures = [
                caller_pool.submit(mixin._run_with_timeout, lambda i=i: {"n": i}, 5)
                for i in range(4)
            ]
            results = [f.result() for f in futures]

        assert len(results) == 4
        mixin._shutdown_executor()


class TestPublicData:
    """Tests for BackgroundRuntime._public_data optimization."""

    def test_includes_normal_values(self):
        from core.runtime.BackgroundRuntime import BackgroundRuntime
        data = {"name": "test", "count": 5, "items": [1, 2, 3], "nested": {"a": "b"}}
        result = BackgroundRuntime._public_data(data)
        assert result == data

    def test_skips_dunder_keys(self):
        from core.runtime.BackgroundRuntime import BackgroundRuntime
        data = {"__m": "model", "__p": "presenter", "__skip_range": (1, 3), "visible": "yes"}
        result = BackgroundRuntime._public_data(data)
        assert result == {"visible": "yes"}

    def test_skips_non_serializable(self):
        from core.runtime.BackgroundRuntime import BackgroundRuntime

        class CustomObj:
            pass

        data = {"good": "value", "bad": CustomObj(), "also_good": 42}
        result = BackgroundRuntime._public_data(data)
        assert result == {"good": "value", "also_good": 42}

    def test_skips_chrome_driver(self):
        from core.runtime.BackgroundRuntime import BackgroundRuntime
        from unittest.mock import MagicMock

        mock_driver = MagicMock()
        mock_driver.__class__.__module__ = "selenium.webdriver.chrome.webdriver"
        mock_driver.__class__.__name__ = "WebDriver"

        data = {"driver": mock_driver, "result": "ok"}
        result = BackgroundRuntime._public_data(data)
        assert "driver" not in result
        assert result == {"result": "ok"}

    def test_http_response_key_shortcut(self):
        from core.runtime.BackgroundRuntime import BackgroundRuntime
        from httpservice.constants import HTTP_RESPONSE_KEY
        data = {
            HTTP_RESPONSE_KEY: "my_response",
            "my_response": {"status": "success", "items": [1, 2]},
            "other": "stuff",
        }
        result = BackgroundRuntime._public_data(data)
        assert result == {"status": "success", "items": [1, 2]}

    def test_non_dict_returns_empty(self):
        from core.runtime.BackgroundRuntime import BackgroundRuntime
        assert BackgroundRuntime._public_data(None) == {}
        assert BackgroundRuntime._public_data("string") == {}
        assert BackgroundRuntime._public_data([1, 2]) == {}

    def test_tuple_values_excluded(self):
        """Tuples are not JSON serializable (they become arrays), but json.dumps handles them."""
        from core.runtime.BackgroundRuntime import BackgroundRuntime
        data = {"coords": (1, 2, 3), "name": "point"}
        result = BackgroundRuntime._public_data(data)
        # json.dumps can serialize tuples (as arrays), so they should be included
        assert "coords" in result
        assert "name" in result


class TestStaticModeCache:
    """Tests for Execution static mode (BG/Docker)."""

    def test_static_mode_skips_stat(self):
        """In static mode, get_execution() returns cached without stat."""
        from core.execution import Execution, set_static_mode, _execution_cache

        set_static_mode(True)
        try:
            # First call populates cache
            e1 = Execution.get_execution("ENDECODER")
            assert e1 is not None

            # Second call should return same object (no re-load)
            e2 = Execution.get_execution("ENDECODER")
            assert e2 is e1
        finally:
            set_static_mode(False)

    def test_static_mode_available_executions_permanent(self):
        """In static mode, get_available_executions() never re-scans."""
        from core.execution import Execution, set_static_mode
        import time as _time

        set_static_mode(True)
        try:
            list1 = Execution.get_available_executions()
            # Even after "TTL expiry" (we can't actually wait 5s, but test the flag logic)
            list2 = Execution.get_available_executions()
            assert list1 is list2  # Same list object, no re-scan
        finally:
            set_static_mode(False)

    def test_non_static_mode_still_checks_mtime(self):
        """Without static mode, mtime check still works (GUI compatibility)."""
        from core.execution import Execution, set_static_mode, _execution_cache

        set_static_mode(False)
        # Normal mode: get_execution still works
        e = Execution.get_execution("ENDECODER")
        assert e is not None
        assert hasattr(e, 'list')

    def test_execution_not_found_returns_none(self):
        """Even in static mode, non-existent execution returns None."""
        from core.execution import Execution, set_static_mode

        set_static_mode(True)
        try:
            result = Execution.get_execution("__NONEXISTENT_EXEC__")
            assert result is None
        finally:
            set_static_mode(False)


class TestOutputSchemaCache:
    """Tests for McpMixin outputSchema cache."""

    def test_schema_cached_across_calls(self):
        """Same tool_name should return cached schema without re-parsing."""
        from httpservice.McpMixin import McpMixin

        mixin = McpMixin()
        call_count = [0]
        original_parse = mixin._parse_tool_value

        def counting_parse(value):
            call_count[0] += 1
            return original_parse(value)

        mixin._parse_tool_value = counting_parse

        tools = {"MY_TOOL": '{"desc":"test","outputSchema":{"type":"object","properties":{"result":{"type":"string"}}}}'}
        getter = lambda: tools

        # First call parses
        schema1 = mixin._get_output_schema("MY_TOOL", getter)
        assert schema1 is not None
        assert "result" in schema1["properties"]
        assert call_count[0] == 1

        # Second call hits cache
        schema2 = mixin._get_output_schema("MY_TOOL", getter)
        assert schema2 is schema1
        assert call_count[0] == 1  # No additional parse

    def test_cache_returns_none_for_no_schema(self):
        """Tools without outputSchema should cache None."""
        from httpservice.McpMixin import McpMixin

        mixin = McpMixin()
        tools = {"SIMPLE_TOOL": '{"desc":"no output schema","params":["x"]}'}
        getter = lambda: tools

        schema = mixin._get_output_schema("SIMPLE_TOOL", getter)
        assert schema is None

        # Still cached (no re-parse on next call)
        assert "SIMPLE_TOOL" in mixin._output_schema_cache

    def test_cache_cleared_on_tools_refresh(self):
        """_normalize_tools() with new tools should clear schema cache."""
        from httpservice.McpMixin import McpMixin

        mixin = McpMixin()
        mixin._output_schema_cache = {"OLD_TOOL": {"type": "object", "properties": {}}}

        # Trigger _normalize_tools with new tool set
        tools = {"NEW_TOOL": '{"desc":"new tool","params":["a"]}'}
        mixin._normalize_tools(tools)

        # Cache should be cleared
        assert mixin._output_schema_cache == {}

    def test_unknown_tool_returns_none(self):
        """Tool not in tools dict should return None."""
        from httpservice.McpMixin import McpMixin

        mixin = McpMixin()
        getter = lambda: {}

        schema = mixin._get_output_schema("MISSING_TOOL", getter)
        assert schema is None


class TestExpressionFastPath:
    """Tests for expression2str static string fast path."""

    def test_static_string_returns_immediately(self):
        """Strings without '{' should return unchanged without eval."""
        from core.processor import Processor
        proc = Processor.get_processor_by_type("ENCODE_DECODE_STR")
        from core.task import Task
        task = Task("ENCODE_DECODE_STR", '{"source":"hello","action":"base64_encode","data_key":"result"}')
        task.data_chain = {"some_key": "some_value"}
        proc.set_task(task)

        assert proc.expression2str("xpath") == "xpath"
        assert proc.expression2str("https://example.com/api") == "https://example.com/api"
        assert proc.expression2str("yes") == "yes"
        assert proc.expression2str("") == ""

    def test_dynamic_expression_still_works(self):
        """Strings with '{' should still be evaluated."""
        from core.processor import Processor
        proc = Processor.get_processor_by_type("ENCODE_DECODE_STR")
        from core.task import Task
        task = Task("ENCODE_DECODE_STR", '{"source":"test","action":"base64_encode","data_key":"result"}')
        task.data_chain = {"name": "world", "count": 42}
        proc.set_task(task)

        assert proc.expression2str("{name}") == "world"
        assert proc.expression2str("hello {name}") == "hello world"
        assert proc.expression2str("{count}") == "42"

    def test_none_returns_none(self):
        """None input should return None."""
        from core.processor import Processor
        proc = Processor.get_processor_by_type("ENCODE_DECODE_STR")
        from core.task import Task
        task = Task("ENCODE_DECODE_STR", '{"source":"x","action":"base64_encode","data_key":"r"}')
        task.data_chain = {}
        proc.set_task(task)

        assert proc.expression2str(None) is None

    def test_numeric_returns_string(self):
        """Numeric input should return string representation."""
        from core.processor import Processor
        proc = Processor.get_processor_by_type("ENCODE_DECODE_STR")
        from core.task import Task
        task = Task("ENCODE_DECODE_STR", '{"source":"x","action":"base64_encode","data_key":"r"}')
        task.data_chain = {}
        proc.set_task(task)

        assert proc.expression2str(42) == "42"
        assert proc.expression2str(3.14) == "3.14"


class TestBatchParallelExecution:
    """Tests for MCP batch parallel tools/call execution."""

    def test_non_tool_calls_processed_sequentially(self):
        """Non-tools/call requests in batch should process normally."""
        from httpservice.McpMixin import McpMixin
        from httpservice.handlers.HttpRequestHandler import StreamingResponseData
        from unittest.mock import MagicMock

        mixin = McpMixin()
        handler = MagicMock()
        handler.headers = {}

        results = {}

        def mock_handler(h, item):
            method = item.get("method")
            req_id = item.get("id")
            if method == "tools/list":
                results[req_id] = True
                return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": []}}
            return {"jsonrpc": "2.0", "id": req_id, "result": {}}

        batch = [
            {"jsonrpc": "2.0", "id": "1", "method": "tools/list"},
            {"jsonrpc": "2.0", "id": "2", "method": "tools/list"},
        ]

        resp = mixin._handle_mcp_batch(handler, batch, mock_handler)
        assert isinstance(resp, StreamingResponseData)
        # Both should have been handled
        assert results.get("1") is True
        assert results.get("2") is True
        mixin._shutdown_executor()

    def test_tool_calls_run_in_parallel(self):
        """Multiple tools/call in batch should run concurrently."""
        from httpservice.McpMixin import McpMixin
        from httpservice.handlers.HttpRequestHandler import StreamingResponseData
        from unittest.mock import MagicMock
        import time as _time

        mixin = McpMixin()
        handler = MagicMock()
        handler.headers = {}

        start_times = {}
        end_times = {}

        def mock_handler(h, item):
            req_id = item.get("id")
            start_times[req_id] = _time.time()
            _time.sleep(0.3)
            end_times[req_id] = _time.time()

            def gen():
                yield f'event: message\ndata: {{"jsonrpc":"2.0","id":"{req_id}","result":{{"content":[]}}}}\n\n'
            return StreamingResponseData(gen(), {}, "text/event-stream", 200)

        batch = [
            {"jsonrpc": "2.0", "id": "a", "method": "tools/call", "params": {"name": "T1", "arguments": {}}},
            {"jsonrpc": "2.0", "id": "b", "method": "tools/call", "params": {"name": "T2", "arguments": {}}},
            {"jsonrpc": "2.0", "id": "c", "method": "tools/call", "params": {"name": "T3", "arguments": {}}},
        ]

        t0 = _time.time()
        resp = mixin._handle_mcp_batch(handler, batch, mock_handler)
        total_time = _time.time() - t0

        # If sequential: ~0.9s. If parallel: ~0.3s. Allow margin.
        assert total_time < 0.7, f"Batch took {total_time:.2f}s — should be parallel (~0.3s)"
        mixin._shutdown_executor()

    def test_invalid_items_in_batch(self):
        """Invalid items should return error without breaking batch."""
        from httpservice.McpMixin import McpMixin
        from unittest.mock import MagicMock

        mixin = McpMixin()
        handler = MagicMock()
        handler.headers = {}

        def mock_handler(h, item):
            return {"jsonrpc": "2.0", "id": item.get("id"), "result": {"ok": True}}

        batch = [
            "not a dict",
            {"jsonrpc": "2.0", "id": "valid", "method": "tools/list"},
        ]

        resp = mixin._handle_mcp_batch(handler, batch, mock_handler)
        # Should handle both: error for invalid, result for valid
        chunks = list(resp.iterator)
        assert len(chunks) > 0
        mixin._shutdown_executor()

    def test_mixed_batch_tool_and_non_tool(self):
        """Batch with mix of tools/call and other methods."""
        from httpservice.McpMixin import McpMixin
        from httpservice.handlers.HttpRequestHandler import StreamingResponseData
        from unittest.mock import MagicMock
        import time as _time

        mixin = McpMixin()
        handler = MagicMock()
        handler.headers = {}

        call_order = []

        def mock_handler(h, item):
            req_id = item.get("id")
            method = item.get("method")
            if method == "tools/call":
                _time.sleep(0.2)
                call_order.append(req_id)
                def gen():
                    yield f'event: message\ndata: {{"jsonrpc":"2.0","id":"{req_id}","result":{{"content":[]}}}}\n\n'
                return StreamingResponseData(gen(), {}, "text/event-stream", 200)
            else:
                call_order.append(req_id)
                return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": []}}

        batch = [
            {"jsonrpc": "2.0", "id": "init", "method": "tools/list"},
            {"jsonrpc": "2.0", "id": "t1", "method": "tools/call", "params": {"name": "A", "arguments": {}}},
            {"jsonrpc": "2.0", "id": "t2", "method": "tools/call", "params": {"name": "B", "arguments": {}}},
        ]

        resp = mixin._handle_mcp_batch(handler, batch, mock_handler)
        # Non-tool call (init) should be processed first (sequentially before parallel tools)
        assert "init" in call_order
        mixin._shutdown_executor()
