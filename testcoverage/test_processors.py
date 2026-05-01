"""Unit tests for individual processors."""

import json
from unittest.mock import patch

import pytest


class TestEncodeDecodeStr:

    def test_base64_encode(self, make_processor):
        chain = {"inbound": "hello", "type": "encode", "algorithms": "base64"}
        proc = make_processor(
            "ENCODE_DECODE_STR",
            '{"type":"encode", "inbound":"hello", "algorithms":"base64", "outbound_key":"result"}',
            chain,
        )
        proc.process()
        assert chain["result"] == "aGVsbG8="

    def test_base64_decode(self, make_processor):
        chain = {"inbound": "aGVsbG8=", "type": "decode", "algorithms": "base64"}
        proc = make_processor(
            "ENCODE_DECODE_STR",
            '{"type":"decode", "inbound":"aGVsbG8=", "algorithms":"base64", "outbound_key":"result"}',
            chain,
        )
        proc.process()
        assert chain["result"] == "hello"

    def test_hexlify_encode(self, make_processor):
        chain = {}
        proc = make_processor(
            "ENCODE_DECODE_STR",
            '{"type":"encode", "inbound":"AB", "algorithms":"hexlify", "outbound_key":"hex_out"}',
            chain,
        )
        proc.process()
        assert chain["hex_out"] == "4142"

    def test_hexlify_decode(self, make_processor):
        chain = {}
        proc = make_processor(
            "ENCODE_DECODE_STR",
            '{"type":"decode", "inbound":"4142", "algorithms":"hexlify", "outbound_key":"hex_out"}',
            chain,
        )
        proc.process()
        assert chain["hex_out"] == "AB"

    def test_base85_roundtrip(self, make_processor):
        chain = {}
        proc = make_processor(
            "ENCODE_DECODE_STR",
            '{"type":"encode", "inbound":"test", "algorithms":"base85", "outbound_key":"encoded"}',
            chain,
        )
        proc.process()
        encoded = chain["encoded"]

        chain2 = {}
        proc2 = make_processor(
            "ENCODE_DECODE_STR",
            json.dumps({"type": "decode", "inbound": encoded, "algorithms": "base85", "outbound_key": "decoded"}),
            chain2,
        )
        proc2.process()
        assert chain2["decoded"] == "test"


class TestWaitSeconds:

    @patch("time.sleep")
    def test_waits_specified_seconds(self, mock_sleep, make_processor):
        proc = make_processor("WAIT_SECONDS", '{"wait_seconds":"3"}', {})
        proc.process()
        mock_sleep.assert_called_once_with(3)

    @patch("time.sleep")
    def test_zero_seconds(self, mock_sleep, make_processor):
        proc = make_processor("WAIT_SECONDS", '{"wait_seconds":"0"}', {})
        proc.process()
        mock_sleep.assert_called_once_with(0)


class TestProcessorDynamicLoading:

    def test_load_valid_processor(self):
        from core.processor import Processor
        proc = Processor.get_processor_by_type("ENCODE_DECODE_STR")
        assert proc is not None
        assert proc.__class__.__name__ == "ENCODE_DECODE_STRProcessor"

    def test_load_wait_seconds(self):
        from core.processor import Processor
        proc = Processor.get_processor_by_type("WAIT_SECONDS")
        assert proc is not None

    def test_cached_loading(self):
        from core.processor import Processor
        proc1 = Processor.get_processor_by_type("ENCODE_DECODE_STR")
        proc2 = Processor.get_processor_by_type("ENCODE_DECODE_STR")
        assert type(proc1) == type(proc2)


class TestHasParam:

    def test_has_param_exists(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"encode", "inbound":"x"}', {})
        assert proc.has_param("type") is True
        assert proc.has_param("inbound") is True

    def test_has_param_missing(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"encode"}', {})
        assert proc.has_param("nonexistent") is False

    def test_has_param_empty_string(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"encode", "empty":""}', {})
        assert proc.has_param("empty") is False

    def test_has_param_non_string_value(self, make_processor):
        proc = make_processor("ENCODE_DECODE_STR", '{"type":"encode", "count":5}', {})
        assert proc.has_param("count") is True
