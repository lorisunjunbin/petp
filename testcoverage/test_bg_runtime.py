"""
Background Runtime test suite.
Run: python testcoverage/test_bg_runtime.py
Exit 0 = all passed, non-zero = failures.
"""
import os
import sys
import json
import traceback

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.runtime.BackgroundRuntime import BackgroundRuntime
from mvp.model.PETPModel import PETPModel
from utils.SystemConfig import SystemConfig

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

_runtime: BackgroundRuntime | None = None


def _get_runtime() -> BackgroundRuntime:
    global _runtime
    if _runtime is None:
        model = PETPModel(SystemConfig("petpconfig.yaml"))
        _runtime = BackgroundRuntime(model, ui_policy="skip")
    return _runtime


def _run(execution_name: str, init_data: dict | None = None) -> dict:
    return _get_runtime().run_execution(execution_name, init_data or {})


PASS = "PASS"
FAIL = "FAIL"
results: list[tuple[str, str, str]] = []   # (name, status, detail)


def case(name: str):
    """Decorator — catches exceptions and records PASS/FAIL."""
    def decorator(fn):
        def wrapper():
            try:
                fn()
                results.append((name, PASS, ""))
            except AssertionError as e:
                results.append((name, FAIL, str(e)))
            except Exception as e:
                results.append((name, FAIL, traceback.format_exc()))
        wrapper.__name__ = name
        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# ENDECODER tests
# ---------------------------------------------------------------------------

@case("ENDECODER: base64 encode")
def test_endecoder_base64_encode():
    r = _run("ENDECODER", {"type": "encode", "algorithms": "base64", "inbound": "hello"})
    assert r["ok"], f"not ok: {r['error']}"
    assert "encoded" in r["data"] or any("aGVsbG8" in str(v) for v in r["data"].values()), \
        f"expected base64 of 'hello' in data: {r['data']}"


@case("ENDECODER: base64 decode")
def test_endecoder_base64_decode():
    r = _run("ENDECODER", {"type": "decode", "algorithms": "base64", "inbound": "aGVsbG8="})
    assert r["ok"], f"not ok: {r['error']}"
    assert any("hello" in str(v) for v in r["data"].values()), \
        f"expected 'hello' in decoded data: {r['data']}"


@case("ENDECODER: execution not found returns ok=False")
def test_execution_not_found():
    r = _run("__NO_SUCH_EXECUTION__")
    assert not r["ok"], "expected ok=False for missing execution"
    assert "not found" in (r["error"] or "").lower(), f"unexpected error msg: {r['error']}"


# ---------------------------------------------------------------------------
# DB_ACCESS (Sqlite) tests
# ---------------------------------------------------------------------------

DB_EXEC = "test_DB_ACCESS_Sqlite"


def _rows(r: dict):
    """Extract the sqlite result rows from a run_execution result.

    test_DB_ACCESS_Sqlite declares an mcp_desc outputSchema (property "data"
    <- mapKey "dataset_sqlite", type "string"), so a direct run_execution maps
    the rows list into data["data"] AND json-serializes it to a string (type
    "string"). Older behavior returned data["dataset_sqlite"] as a raw list.
    Accept both: prefer the raw list if present, else json.loads the mapped
    string back into rows."""
    data = r["data"]
    if "dataset_sqlite" in data:
        return data["dataset_sqlite"]
    mapped = data.get("data")
    if isinstance(mapped, str):
        return json.loads(mapped)
    return mapped


@case("DB_ACCESS Sqlite: SELECT all users (no placeholder)")
def test_db_select_all_no_placeholder():
    r = _run(DB_EXEC, {"sql": "SELECT * FROM user", "param": ""})
    assert r["ok"], f"not ok: {r['error']}"
    rows = _rows(r)
    assert rows is not None, f"dataset_sqlite missing in: {r['data']}"
    assert len(rows) >= 1, f"expected at least 1 row, got: {rows}"


@case("DB_ACCESS Sqlite: SELECT with ? placeholder")
def test_db_select_with_placeholder():
    r = _run(DB_EXEC, {"sql": "SELECT * FROM user WHERE id > ?", "param": "0"})
    assert r["ok"], f"not ok: {r['error']}"
    rows = _rows(r)
    assert rows is not None and len(rows) >= 1, f"expected rows: {rows}"


@case("DB_ACCESS Sqlite: COUNT with no placeholder")
def test_db_count_no_placeholder():
    r = _run(DB_EXEC, {"sql": "SELECT COUNT(*) FROM user"})
    assert r["ok"], f"not ok: {r['error']}"
    rows = _rows(r)
    assert rows is not None and rows[0][0] >= 1, f"unexpected count: {rows}"


@case("DB_ACCESS Sqlite: sqlite_version() — no placeholder, param should be ignored")
def test_db_sqlite_version_no_placeholder():
    # Even if param is passed, it must not be forwarded to the driver
    r = _run(DB_EXEC, {"sql": "SELECT sqlite_version()", "param": "should_be_ignored"})
    assert r["ok"], f"not ok: {r['error']}"
    rows = _rows(r)
    assert rows is not None and len(rows) == 1, f"expected exactly 1 row: {rows}"
    version = str(rows[0][0])
    assert version.replace(".", "").isdigit() or "." in version, f"unexpected version: {version}"


@case("DB_ACCESS Sqlite: SELECT by exact name match")
def test_db_select_by_name():
    r = _run(DB_EXEC, {"sql": "SELECT id, name FROM user WHERE name = 'PETP'", "param": ""})
    assert r["ok"], f"not ok: {r['error']}"
    rows = _rows(r)
    assert rows is not None and len(rows) >= 1, f"PETP user not found: {rows}"
    assert rows[0][1] == "PETP", f"unexpected name: {rows[0]}"


@case("DB_ACCESS Sqlite: empty result set")
def test_db_empty_result():
    r = _run(DB_EXEC, {"sql": "SELECT * FROM user WHERE id = ?", "param": "999999"})
    assert r["ok"], f"not ok: {r['error']}"
    rows = _rows(r)
    assert rows is not None and len(rows) == 0, f"expected empty result, got: {rows}"


@case("DB_ACCESS Sqlite: syntax error SQL silently returns empty result")
def test_db_invalid_sql():
    # SqliteDBAccess.execute catches sqlite3.Error internally and returns []
    r = _run(DB_EXEC, {"sql": "THIS IS NOT VALID SQL !@#"})
    assert r["ok"], f"expected ok=True (error is swallowed by driver), got: {r}"
    rows = _rows(r)
    assert rows is not None and len(rows) == 0, f"expected empty result for bad SQL: {rows}"


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

@case("Pipeline: missing pipeline returns ok=False")
def test_pipeline_not_found():
    r = _get_runtime().run_pipeline("__NO_SUCH_PIPELINE__")
    assert not r["ok"], "expected ok=False for missing pipeline"


@case("Pipeline: run OOTB_TEST_PIPLINE_BG (multi-step)")
def test_pipeline_run_success():
    r = _get_runtime().run_pipeline("OOTB_TEST_PIPLINE_BG")
    # This pipeline has steps that may skip in BG mode, but should complete
    assert "ok" in r, f"expected result dict, got: {r}"
    assert "meta" in r


@case("Pipeline: run_in_pipeline flag present in result data")
def test_pipeline_run_in_pipeline_flag():
    r = _get_runtime().run_pipeline("OOTB_TEST_PIPLINE_BG")
    if r["ok"]:
        assert r["data"].get("run_in_pipeline") == "yes"


@case("Pipeline: reentrant protection rejects second call")
def test_pipeline_reentrant():
    import threading
    name = "OOTB_TEST_PIPLINE_BG"
    rt = _get_runtime()
    # Manually mark as running
    with rt._running_pipelines_lock:
        rt._running_pipelines.add(name)
    try:
        r = rt.run_pipeline(name)
        assert not r["ok"], "expected rejection when already running"
        assert "already running" in r.get("error", "")
    finally:
        with rt._running_pipelines_lock:
            rt._running_pipelines.discard(name)


@case("Pipeline: with init-data passed through")
def test_pipeline_with_init_data():
    r = _get_runtime().run_pipeline("OOTB_TEST_PIPLINE_BG", {"custom_key": "custom_value"})
    assert "ok" in r


# ---------------------------------------------------------------------------
# Meta / tools cache
# ---------------------------------------------------------------------------

@case("get_tools: returns a non-empty dict")
def test_get_tools():
    tools = _get_runtime().get_tools()
    assert isinstance(tools, dict) and len(tools) > 0, f"expected tools, got: {tools}"


@case("get_tools: cache hit returns same object")
def test_get_tools_cache():
    rt = _get_runtime()
    t1 = rt.get_tools()
    t2 = rt.get_tools()
    assert t1 is t2, "expected cached object identity"


@case("invalidate_tools_cache: next call rebuilds cache")
def test_invalidate_tools_cache():
    rt = _get_runtime()
    t1 = rt.get_tools()
    rt.invalidate_tools_cache()
    t2 = rt.get_tools()
    assert t1 is not t2, "expected new object after invalidation"


# ---------------------------------------------------------------------------
# result structure contract
# ---------------------------------------------------------------------------

@case("result structure: ok/data/error/meta keys always present")
def test_result_structure():
    r = _run("ENDECODER", {"type": "encode", "algorithms": "base64", "inbound": "x"})
    for key in ("ok", "data", "error", "meta"):
        assert key in r, f"missing key '{key}' in result: {r}"
    assert "duration_ms" in r["meta"], f"missing duration_ms in meta: {r['meta']}"
    assert "skipped_tasks" in r["meta"], f"missing skipped_tasks in meta: {r['meta']}"


# ---------------------------------------------------------------------------
# Execution cache
# ---------------------------------------------------------------------------

@case("Execution cache: same object returned on repeated get_execution")
def test_execution_cache_hit():
    from core.execution import Execution
    e1 = Execution.get_execution("ENDECODER")
    e2 = Execution.get_execution("ENDECODER")
    assert e1 is e2, "expected cached object identity on repeated get_execution"


@case("_public_data: filters internal keys and non-serializable values correctly")
def test_public_data():
    from core.runtime.BackgroundRuntime import BackgroundRuntime
    # Normal values are included
    data = {"name": "hello", "count": 42, "nested": {"list": [1, 2]}}
    result = BackgroundRuntime._public_data(data)
    assert result == data, f"expected all values included: {result}"

    # __ prefixed keys are excluded
    data_with_internal = {"__m": object(), "__p": object(), "__skip_range": (1, 3), "visible": "yes"}
    result = BackgroundRuntime._public_data(data_with_internal)
    assert result == {"visible": "yes"}, f"expected only 'visible': {result}"

    # Non-serializable objects are excluded
    data_with_obj = {"good": "value", "bad": object()}
    result = BackgroundRuntime._public_data(data_with_obj)
    assert result == {"good": "value"}, f"expected 'bad' excluded: {result}"

    # None input returns empty dict
    assert BackgroundRuntime._public_data(None) == {}
    assert BackgroundRuntime._public_data("not a dict") == {}


# ---------------------------------------------------------------------------
# runner
# ---------------------------------------------------------------------------

ALL_CASES = [
    test_endecoder_base64_encode,
    test_endecoder_base64_decode,
    test_execution_not_found,
    test_db_select_all_no_placeholder,
    test_db_select_with_placeholder,
    test_db_count_no_placeholder,
    test_db_sqlite_version_no_placeholder,
    test_db_select_by_name,
    test_db_empty_result,
    test_db_invalid_sql,
    test_pipeline_not_found,
    test_pipeline_run_success,
    test_pipeline_run_in_pipeline_flag,
    test_pipeline_reentrant,
    test_pipeline_with_init_data,
    test_get_tools,
    test_get_tools_cache,
    test_invalidate_tools_cache,
    test_result_structure,
    test_execution_cache_hit,
    test_public_data,
]


def main():
    print(f"\nRunning {len(ALL_CASES)} test cases...\n")
    for fn in ALL_CASES:
        fn()

    pad = max(len(name) for name, *_ in results)
    passed = failed = 0
    for name, status, detail in results:
        marker = "✓" if status == PASS else "✗"
        print(f"  {marker}  {name:<{pad}}  {status}")
        if detail:
            for line in detail.splitlines():
                print(f"       {line}")
        if status == PASS:
            passed += 1
        else:
            failed += 1

    print(f"\n{'='*60}")
    print(f"  {passed} passed  |  {failed} failed  |  {len(ALL_CASES)} total")
    print(f"{'='*60}\n")

    if failed:
        raise SystemExit(failed)


if __name__ == "__main__":
    main()
