"""Tests for filter_unsupported_kwargs — guards against anthropic SDK builds
whose messages.create signature omits temperature/top_p and has no **kwargs."""

from core.processors.sub.llm.llm_helpers import filter_unsupported_kwargs


class TestFilterUnsupportedKwargs:

    def test_drops_param_not_in_signature(self):
        # Mimics the custom anthropic build: no temperature, no **kwargs.
        def create(*, model, messages, max_tokens, system=None):
            ...
        params = {"model": "m", "messages": [], "max_tokens": 10,
                  "temperature": 0.7, "system": "s"}
        out = filter_unsupported_kwargs(create, params)
        assert "temperature" not in out
        assert out == {"model": "m", "messages": [], "max_tokens": 10, "system": "s"}

    def test_keeps_all_when_var_kwargs_present(self):
        # Normal upstream SDK accepts **kwargs → nothing dropped.
        def create(*, model, messages, max_tokens, **kwargs):
            ...
        params = {"model": "m", "messages": [], "max_tokens": 10, "temperature": 0.7}
        out = filter_unsupported_kwargs(create, params)
        assert out == params

    def test_keeps_temperature_when_signature_has_it(self):
        def create(*, model, messages, max_tokens, temperature=1.0):
            ...
        params = {"model": "m", "messages": [], "max_tokens": 10, "temperature": 0.3}
        out = filter_unsupported_kwargs(create, params)
        assert out["temperature"] == 0.3

    def test_passthrough_when_signature_uninspectable(self):
        # Builtins like max() raise ValueError under inspect.signature →
        # helper must pass params through unchanged rather than crash.
        import inspect
        with_pytest_raises = False
        try:
            inspect.signature(max)
        except (TypeError, ValueError):
            with_pytest_raises = True
        assert with_pytest_raises, "precondition: max() must be uninspectable"
        out = filter_unsupported_kwargs(max, {"temperature": 0.7, "x": 1})
        assert out == {"temperature": 0.7, "x": 1}

    def test_matches_custom_anthropic_shape(self):
        # Exact repro of the reported bug: 1.6.0-style signature without
        # temperature, with the custom gateway fields, no **kwargs.
        def create(*, max_tokens, messages, model, system=None,
                   workspace_id=None, inference_geo=None):
            ...
        params = {"model": "glm", "messages": [], "max_tokens": 4096,
                  "temperature": 0, "system": "hi"}
        out = filter_unsupported_kwargs(create, params)
        assert "temperature" not in out
        assert out == {"model": "glm", "messages": [], "max_tokens": 4096, "system": "hi"}
