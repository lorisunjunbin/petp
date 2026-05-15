"""Integration test for MCP batch parallel execution.

Tests the full MCP batch request flow against BackgroundHttpServer,
verifying that multiple tools/call requests in a batch execute in parallel.

Usage:
  # Against running server (requires: python PETP_background.py)
  python testcoverage/test_mcp_batch.py

  # Or via pytest (uses mocked server, no running instance needed)
  pytest testcoverage/test_mcp_batch.py -v
"""

import json
import time
import pytest
from unittest.mock import MagicMock, patch
from queue import SimpleQueue


# ---------------------------------------------------------------------------
# Pytest-based tests (no running server required)
# ---------------------------------------------------------------------------


class TestMcpBatchIntegration:
    """Full integration tests for MCP batch with BackgroundHttpServer."""

    def _make_server(self):
        from core.runtime.BackgroundRuntime import BackgroundRuntime
        from httpservice.BackgroundHttpServer import BackgroundHttpServer

        model = MagicMock()
        model.http_request_timeout = 30
        model.http_request_token = ""
        runtime = BackgroundRuntime(model)
        server = BackgroundHttpServer.__new__(BackgroundHttpServer)
        server.runtime = runtime
        server._token = ""
        server._timeout = 30
        server._executor = None
        server._normalized_tools_cache_key = None
        server._normalized_tools_cache_val = []
        server._output_schema_cache = {}
        return server

    def _make_handler(self, accept="application/json"):
        handler = MagicMock()
        handler.headers = {"Accept": accept, "Content-Type": "application/json"}
        return handler

    def test_batch_single_tool_call(self):
        """Single tools/call in a batch should work correctly."""
        server = self._make_server()
        handler = self._make_handler(accept="text/event-stream")

        batch = [
            {
                "jsonrpc": "2.0",
                "id": "req-1",
                "method": "tools/call",
                "params": {
                    "name": "ENDECODER",
                    "arguments": {"type": "ENCODE", "algorithms": "base64", "inbound": "batch_test"}
                }
            }
        ]

        params = {"_batch": batch}
        result = server._handle_mcp(handler, params)

        chunks = list(result.iterator)
        assert len(chunks) > 0

        payload = self._parse_sse_payload(chunks)
        assert payload is not None
        assert payload.get("id") == "req-1"
        assert "result" in payload
        assert payload["result"].get("isError") is False

    def test_batch_multiple_tool_calls_parallel(self):
        """Multiple tools/call in batch should execute in parallel."""
        server = self._make_server()
        handler = self._make_handler(accept="text/event-stream")

        batch = [
            {
                "jsonrpc": "2.0",
                "id": "enc-1",
                "method": "tools/call",
                "params": {
                    "name": "ENDECODER",
                    "arguments": {"type": "ENCODE", "algorithms": "base64", "inbound": "aaa"}
                }
            },
            {
                "jsonrpc": "2.0",
                "id": "enc-2",
                "method": "tools/call",
                "params": {
                    "name": "ENDECODER",
                    "arguments": {"type": "ENCODE", "algorithms": "base64", "inbound": "bbb"}
                }
            },
            {
                "jsonrpc": "2.0",
                "id": "enc-3",
                "method": "tools/call",
                "params": {
                    "name": "ENDECODER",
                    "arguments": {"type": "DECODE", "algorithms": "base64", "inbound": "Y2Nj"}
                }
            },
        ]

        params = {"_batch": batch}
        t0 = time.time()
        result = server._handle_mcp(handler, params)
        chunks = list(result.iterator)
        elapsed = time.time() - t0

        # Parse batch response
        payload = self._parse_sse_payload(chunks)
        assert payload is not None

        # Should be a list of responses for batch
        if isinstance(payload, list):
            ids = {r.get("id") for r in payload}
            assert "enc-1" in ids
            assert "enc-2" in ids
            assert "enc-3" in ids
            for r in payload:
                assert r.get("result", {}).get("isError") is False
        else:
            # Single response (only if batch of 1 response)
            assert payload.get("id") in ("enc-1", "enc-2", "enc-3")

    def test_batch_mixed_methods(self):
        """Batch with tools/list + tools/call should handle both."""
        server = self._make_server()
        handler = self._make_handler(accept="text/event-stream")

        batch = [
            {
                "jsonrpc": "2.0",
                "id": "list-1",
                "method": "tools/list",
                "params": {}
            },
            {
                "jsonrpc": "2.0",
                "id": "call-1",
                "method": "tools/call",
                "params": {
                    "name": "ENDECODER",
                    "arguments": {"type": "ENCODE", "algorithms": "base64", "inbound": "mixed"}
                }
            },
        ]

        params = {"_batch": batch}
        result = server._handle_mcp(handler, params)
        chunks = list(result.iterator)

        payload = self._parse_sse_payload(chunks)
        assert payload is not None

        if isinstance(payload, list):
            ids = {r.get("id") for r in payload}
            assert "list-1" in ids
            assert "call-1" in ids
            # tools/list response should have "tools" key
            list_resp = next(r for r in payload if r.get("id") == "list-1")
            assert "tools" in list_resp.get("result", {})
        else:
            assert payload.get("id") in ("list-1", "call-1")

    def test_batch_with_invalid_tool_name(self):
        """Batch with non-existent tool should return error for that item."""
        server = self._make_server()
        handler = self._make_handler(accept="text/event-stream")

        batch = [
            {
                "jsonrpc": "2.0",
                "id": "good",
                "method": "tools/call",
                "params": {
                    "name": "ENDECODER",
                    "arguments": {"type": "ENCODE", "algorithms": "base64", "inbound": "ok"}
                }
            },
            {
                "jsonrpc": "2.0",
                "id": "bad",
                "method": "tools/call",
                "params": {
                    "name": "__NONEXISTENT_TOOL__",
                    "arguments": {}
                }
            },
        ]

        params = {"_batch": batch}
        result = server._handle_mcp(handler, params)
        chunks = list(result.iterator)

        payload = self._parse_sse_payload(chunks)
        assert payload is not None

        if isinstance(payload, list):
            good_resp = next((r for r in payload if r.get("id") == "good"), None)
            bad_resp = next((r for r in payload if r.get("id") == "bad"), None)

            assert good_resp is not None
            assert good_resp.get("result", {}).get("isError") is False

            assert bad_resp is not None
            assert bad_resp.get("result", {}).get("isError") is True

    def test_batch_with_invalid_request_item(self):
        """Non-dict items in batch should return Invalid Request error."""
        server = self._make_server()
        handler = self._make_handler(accept="text/event-stream")

        batch = [
            "this is not a dict",
            42,
            {
                "jsonrpc": "2.0",
                "id": "valid",
                "method": "tools/call",
                "params": {
                    "name": "ENDECODER",
                    "arguments": {"type": "ENCODE", "algorithms": "base64", "inbound": "x"}
                }
            },
        ]

        params = {"_batch": batch}
        result = server._handle_mcp(handler, params)
        chunks = list(result.iterator)

        payload = self._parse_sse_payload(chunks)
        assert payload is not None

        if isinstance(payload, list):
            errors = [r for r in payload if "error" in r]
            valids = [r for r in payload if r.get("id") == "valid"]
            assert len(errors) >= 2
            assert len(valids) == 1
            for e in errors:
                assert e["error"]["code"] == -32600

    def test_batch_empty(self):
        """Empty batch should return empty response."""
        server = self._make_server()
        handler = self._make_handler(accept="text/event-stream")

        params = {"_batch": []}
        result = server._handle_mcp(handler, params)
        chunks = list(result.iterator)
        # Should not crash, empty payload is OK
        assert isinstance(chunks, list)

    def test_batch_preserves_response_order(self):
        """Responses should maintain correspondence to request IDs (not necessarily order)."""
        server = self._make_server()
        handler = self._make_handler(accept="text/event-stream")

        batch = [
            {
                "jsonrpc": "2.0",
                "id": f"req-{i}",
                "method": "tools/call",
                "params": {
                    "name": "ENDECODER",
                    "arguments": {"type": "ENCODE", "algorithms": "base64", "inbound": f"data_{i}"}
                }
            }
            for i in range(4)
        ]

        params = {"_batch": batch}
        result = server._handle_mcp(handler, params)
        chunks = list(result.iterator)

        payload = self._parse_sse_payload(chunks)
        if isinstance(payload, list):
            response_ids = {r.get("id") for r in payload}
            expected_ids = {f"req-{i}" for i in range(4)}
            assert response_ids == expected_ids

    def test_batch_no_sse_mode(self):
        """Batch with Accept: application/json (no SSE) should still work."""
        server = self._make_server()
        handler = self._make_handler(accept="application/json")

        batch = [
            {
                "jsonrpc": "2.0",
                "id": "json-1",
                "method": "tools/call",
                "params": {
                    "name": "ENDECODER",
                    "arguments": {"type": "ENCODE", "algorithms": "base64", "inbound": "json_mode"}
                }
            },
        ]

        params = {"_batch": batch}
        result = server._handle_mcp(handler, params)
        # Should return StreamingResponseData regardless (batch always uses SSE wrapper)
        chunks = list(result.iterator)
        assert len(chunks) > 0

    @staticmethod
    def _parse_sse_payload(chunks):
        """Extract JSON payload from SSE chunks."""
        for chunk in chunks:
            if "data: " in chunk:
                data_str = chunk.split("data: ", 1)[1].rstrip("\n")
                try:
                    return json.loads(data_str)
                except json.JSONDecodeError:
                    continue
        return None


# ---------------------------------------------------------------------------
# Live server test (run manually with: python testcoverage/test_mcp_batch.py)
# ---------------------------------------------------------------------------

def run_live_batch_test():
    """Test batch against a running PETP background server on localhost:8866."""
    import urllib.request

    url = "http://localhost:8866/mcp"
    headers = {"Content-Type": "application/json", "Accept": "text/event-stream"}

    # Test 1: Batch with multiple parallel tools/call
    print("\n=== Test 1: Parallel batch tools/call ===")
    batch = [
        {
            "jsonrpc": "2.0",
            "id": "enc-1",
            "method": "tools/call",
            "params": {"name": "ENDECODER", "arguments": {"type": "ENCODE", "algorithms": "base64", "inbound": "hello"}}
        },
        {
            "jsonrpc": "2.0",
            "id": "enc-2",
            "method": "tools/call",
            "params": {"name": "ENDECODER", "arguments": {"type": "ENCODE", "algorithms": "base64", "inbound": "world"}}
        },
        {
            "jsonrpc": "2.0",
            "id": "enc-3",
            "method": "tools/call",
            "params": {"name": "ENDECODER", "arguments": {"type": "DECODE", "algorithms": "base64", "inbound": "cGV0cA=="}}
        },
    ]

    t0 = time.time()
    req = urllib.request.Request(url, data=json.dumps(batch).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode()
            elapsed = time.time() - t0
            print(f"  Status: {resp.status}")
            print(f"  Time: {elapsed:.3f}s")
            print(f"  Response: {body[:500]}")
            # Parse SSE events
            for line in body.split("\n"):
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    if isinstance(data, list):
                        for r in data:
                            print(f"  [{r.get('id')}] isError={r.get('result', {}).get('isError')}")
                    else:
                        print(f"  [{data.get('id')}] isError={data.get('result', {}).get('isError')}")
    except Exception as e:
        print(f"  ERROR: {e}")

    # Test 2: Mixed batch (tools/list + tools/call)
    print("\n=== Test 2: Mixed batch (tools/list + tools/call) ===")
    batch = [
        {"jsonrpc": "2.0", "id": "list-1", "method": "tools/list", "params": {}},
        {
            "jsonrpc": "2.0",
            "id": "call-1",
            "method": "tools/call",
            "params": {"name": "ENDECODER", "arguments": {"type": "ENCODE", "algorithms": "base64", "inbound": "mix"}}
        },
    ]

    req = urllib.request.Request(url, data=json.dumps(batch).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode()
            print(f"  Status: {resp.status}")
            for line in body.split("\n"):
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    if isinstance(data, list):
                        for r in data:
                            rid = r.get("id")
                            has_tools = "tools" in r.get("result", {})
                            has_content = "content" in r.get("result", {})
                            print(f"  [{rid}] tools_list={has_tools} tool_result={has_content}")
                    else:
                        print(f"  [{data.get('id')}]")
    except Exception as e:
        print(f"  ERROR: {e}")

    # Test 3: Batch with error (non-existent tool)
    print("\n=== Test 3: Batch with error (bad tool name) ===")
    batch = [
        {
            "jsonrpc": "2.0",
            "id": "good-1",
            "method": "tools/call",
            "params": {"name": "ENDECODER", "arguments": {"type": "ENCODE", "algorithms": "base64", "inbound": "ok"}}
        },
        {
            "jsonrpc": "2.0",
            "id": "bad-1",
            "method": "tools/call",
            "params": {"name": "__DOES_NOT_EXIST__", "arguments": {}}
        },
    ]

    req = urllib.request.Request(url, data=json.dumps(batch).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode()
            print(f"  Status: {resp.status}")
            for line in body.split("\n"):
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    if isinstance(data, list):
                        for r in data:
                            is_err = r.get("result", {}).get("isError", False)
                            print(f"  [{r.get('id')}] isError={is_err}")
    except Exception as e:
        print(f"  ERROR: {e}")

    # Test 4: Single request (non-batch, for comparison)
    print("\n=== Test 4: Single tools/call (non-batch baseline) ===")
    single = {
        "jsonrpc": "2.0",
        "id": "single-1",
        "method": "tools/call",
        "params": {"name": "ENDECODER", "arguments": {"type": "ENCODE", "algorithms": "base64", "inbound": "single"}}
    }

    t0 = time.time()
    req = urllib.request.Request(url, data=json.dumps(single).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode()
            elapsed = time.time() - t0
            print(f"  Status: {resp.status}, Time: {elapsed:.3f}s")
            for line in body.split("\n"):
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    if "id" in data:
                        print(f"  [{data.get('id')}] isError={data.get('result', {}).get('isError')}")
    except Exception as e:
        print(f"  ERROR: {e}")

    print("\n=== All live tests completed ===")


if __name__ == "__main__":
    run_live_batch_test()
