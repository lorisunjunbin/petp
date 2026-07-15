"""PETP Portable Runtime entry. Copy the whole portable/ dir into your project.

    from portable.petp_run import run
    result = run("T_Supplier_Creation", {"supplier_name": "ACME"})

NOTE: importing this module runs os.chdir() into the portable/ directory
(the "convention cwd" design) and does NOT restore the caller's cwd.
"""
import os, sys

_HERE = os.path.dirname(os.path.realpath(__file__))
os.chdir(_HERE)                       # make realpath('.')/realpath('core') land in portable/
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from core.runtime.BackgroundRuntime import BackgroundRuntime

_logging_ready = False


def _ensure_logging():
    """Configure PETP logging once (console + rotating file at portable/log/).
    Skipped when the caller opts out — importing as a library should not clobber
    the caller's own logging config (Logger.init clears root handlers)."""
    global _logging_ready
    if _logging_ready:
        return
    import utils.Logger as Logger
    Logger.init("petp-portable")
    _logging_ready = True


def run(execution_name: str, init_data: dict = None, setup_logging: bool = True) -> dict:
    """Run one Execution headlessly. Returns {"ok","data","error","meta"}.

    setup_logging: when True (default) configure PETP console+file logging so the
        run's INFO logs are visible. Pass False when embedding as a library and
        you manage logging yourself (avoids clearing your root handlers).
    """
    if setup_logging:
        _ensure_logging()
    os.environ.setdefault('PETP_HEADLESS', 'true')
    runtime = BackgroundRuntime(model=None)
    return runtime.run_execution(execution_name, init_data or {})


if __name__ == '__main__':
    import json
    name = sys.argv[1] if len(sys.argv) > 1 else 'SMOKE_TEST'
    data = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    print(json.dumps(run(name, data), ensure_ascii=False, default=str))
