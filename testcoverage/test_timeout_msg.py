"""Unit tests for the timeout_msg / soft-skip logging helpers on Processor:
resolve_timeout_msg(), fail_or_skip(..., timeout_msg=), and log_noop().

These cover the business-context-on-locator-failure feature used by
FIND_THEN_CLICK / FIND_THEN_KEYIN, without touching a real browser.
"""

import logging

import pytest


class TestResolveTimeoutMsg:

    def test_absent_param_returns_empty(self, make_processor):
        proc = make_processor("FIND_THEN_CLICK", '{"identity":"//x"}', {})
        assert proc.resolve_timeout_msg(10) == ""

    def test_resolves_data_chain_and_timeout_var(self, make_processor):
        proc = make_processor(
            "FIND_THEN_CLICK",
            '{"timeout_msg":"Can not find the supplier {supplier_name} in {timeout} seconds."}',
            {"supplier_name": "ABC"},
        )
        assert proc.resolve_timeout_msg(10) == "Can not find the supplier ABC in 10 seconds."

    def test_timeout_var_shadows_chain_key(self, make_processor):
        # A pre-existing data_chain 'timeout' key must NOT override the local one.
        proc = make_processor("FIND_THEN_CLICK", '{"timeout_msg":"waited {timeout}s"}', {"timeout": 999})
        assert proc.resolve_timeout_msg(10) == "waited 10s"

    def test_does_not_mutate_data_chain(self, make_processor):
        chain = {"supplier_name": "ABC"}
        proc = make_processor("FIND_THEN_CLICK", '{"timeout_msg":"{timeout}"}', chain)
        proc.resolve_timeout_msg(10)
        assert "timeout" not in chain

    def test_plain_message_without_expression(self, make_processor):
        proc = make_processor("FIND_THEN_CLICK", '{"timeout_msg":"submit button missing"}', {})
        assert proc.resolve_timeout_msg(5) == "submit button missing"


class TestFailOrSkip:

    def test_raises_with_prefix(self, make_processor):
        proc = make_processor("FIND_THEN_CLICK", '{"identity":"//x"}', {})
        with pytest.raises(Exception) as ei:
            proc.fail_or_skip("not found", False, prefix="FIND_THEN_CLICK")
        assert "FIND_THEN_CLICK: not found" in str(ei.value)

    def test_raise_appends_timeout_msg(self, make_processor):
        proc = make_processor("FIND_THEN_CLICK", '{"identity":"//x"}', {})
        with pytest.raises(Exception) as ei:
            proc.fail_or_skip("not found", False, prefix="FIND_THEN_CLICK", timeout_msg="供应商 ABC 未找到")
        msg = str(ei.value)
        assert "not found" in msg and "供应商 ABC 未找到" in msg

    def test_skip_does_not_raise_and_returns_none(self, make_processor):
        proc = make_processor("FIND_THEN_CLICK", '{"identity":"//x"}', {})
        assert proc.fail_or_skip("not found", True, prefix="FIND_THEN_CLICK", timeout_msg="ignored") is None

    def test_skip_omits_timeout_msg_from_noop_log(self, make_processor, caplog):
        proc = make_processor("FIND_THEN_CLICK", '{"identity":"//x"}', {})
        with caplog.at_level(logging.WARNING):
            proc.fail_or_skip("not found", True, prefix="FIND_THEN_CLICK", timeout_msg="should-not-appear")
        text = caplog.text
        assert "[NOOP]" in text
        assert "not found" in text
        assert "should-not-appear" not in text  # timeout_msg is only for the raise path


class TestLogNoop:

    def test_emits_noop_warning_with_class_name(self, make_processor, caplog):
        proc = make_processor("FIND_THEN_CLICK", '{"identity":"//x"}', {})
        with caplog.at_level(logging.WARNING):
            proc.log_noop("element not found -- CLICK NOT PERFORMED")
        assert "[NOOP]" in caplog.text
        assert "FIND_THEN_CLICKProcessor" in caplog.text
        assert "element not found -- CLICK NOT PERFORMED" in caplog.text
        assert any(r.levelno == logging.WARNING for r in caplog.records)
