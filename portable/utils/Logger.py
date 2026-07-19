import contextvars
import logging
import sys
import threading
import uuid

from logging.handlers import RotatingFileHandler
from logging import StreamHandler

from utils.OSUtils import OSUtils

_CONSOLE_FORMAT = '%(asctime)s <%(levelname)s> [%(threadName)s] [%(traceId)s] %(name)s:%(lineno)d - %(message)s'
_FILE_FORMAT    = '%(asctime)s <%(levelname)s> [%(threadName)s] [%(traceId)s] %(filename)s:%(lineno)d - %(message)s'
_DATE_FORMAT    = '%Y-%m-%d %H:%M:%S'

# Per-execution trace id, propagated through the (thread-pool) call chain via a
# ContextVar so concurrent HTTP/MCP requests each keep their own id. Injected
# into every LogRecord by TraceFilter, so existing logging.xxx() calls need no
# change. Default '-' means "no trace id set" (e.g. startup logs).
_trace_id: contextvars.ContextVar = contextvars.ContextVar('trace_id', default='-')


def set_trace_id(trace_id: str = None) -> str:
    """Set the trace id for the current context. Returns the effective id.

    When ``trace_id`` is falsy: keep an id already set on this context (so a
    pipeline's id survives its per-step run_execution(None) calls), otherwise
    generate a short random one. An explicit ``trace_id`` always overrides.
    """
    tid = str(trace_id).strip() if trace_id else ''
    if not tid:
        current = _trace_id.get()
        tid = current if current and current != '-' else uuid.uuid4().hex[:8]
    _trace_id.set(tid)
    return tid


def get_trace_id() -> str:
    return _trace_id.get()


class TraceFilter(logging.Filter):
    """Attach the current context's trace id to every record as ``traceId``."""

    def filter(self, record):
        record.traceId = _trace_id.get()
        return True


def init(app, level=logging.INFO):
    formatter_console = logging.Formatter(_CONSOLE_FORMAT, datefmt=_DATE_FORMAT)
    formatter_file    = logging.Formatter(_FILE_FORMAT,    datefmt=_DATE_FORMAT)

    trace_filter = TraceFilter()

    console_handler = StreamHandler()
    console_handler.setFormatter(formatter_console)
    console_handler.addFilter(trace_filter)

    file_handler = RotatingFileHandler(
        filename=OSUtils.get_log_file_path(app),
        mode='a',
        maxBytes=10 * 1024 * 1024,
        backupCount=2,
        encoding='utf-8',
        delay=False,
    )
    file_handler.setFormatter(formatter_file)
    file_handler.addFilter(trace_filter)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(console_handler)
    root.addHandler(file_handler)

    patch_threading_excepthook()
    sys.excepthook = handle_unhandled_exception


def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))


def patch_threading_excepthook():
    """Route uncaught thread exceptions through sys.excepthook for unified logging."""
    old_init = threading.Thread.__init__

    def new_init(self, *args, **kwargs):
        old_init(self, *args, **kwargs)
        old_run = self.run

        def run_with_our_excepthook(*args, **kwargs):
            try:
                old_run(*args, **kwargs)
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception:
                sys.excepthook(*sys.exc_info())

        self.run = run_with_our_excepthook

    threading.Thread.__init__ = new_init
