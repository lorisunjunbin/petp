import logging
import sys
import threading

from logging.handlers import RotatingFileHandler
from logging import StreamHandler

from utils.OSUtils import OSUtils

_CONSOLE_FORMAT = '%(asctime)s <%(levelname)s> [%(threadName)s] %(name)s:%(lineno)d - %(message)s'
_FILE_FORMAT    = '%(asctime)s <%(levelname)s> [%(threadName)s] %(filename)s:%(lineno)d - %(message)s'
_DATE_FORMAT    = '%Y-%m-%d %H:%M:%S'


def init(app, level=logging.INFO):
    formatter_console = logging.Formatter(_CONSOLE_FORMAT, datefmt=_DATE_FORMAT)
    formatter_file    = logging.Formatter(_FILE_FORMAT,    datefmt=_DATE_FORMAT)

    console_handler = StreamHandler()
    console_handler.setFormatter(formatter_console)

    file_handler = RotatingFileHandler(
        filename=OSUtils.get_log_file_path(app),
        mode='a',
        maxBytes=10 * 1024 * 1024,
        backupCount=2,
        encoding='utf-8',
        delay=False,
    )
    file_handler.setFormatter(formatter_file)

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
