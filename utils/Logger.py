import logging
import sys
import threading

from logging.handlers import RotatingFileHandler
from logging import StreamHandler


from utils.DateUtil import DateUtil
from utils.OSUtils import OSUtils


def init(app):
    logging.basicConfig(
        level=logging.INFO,
        encoding='utf-8',
        datefmt='%m/%d/%Y %I:%M:%S',
        format='<%(levelname)s>[ %(threadName)s ] - %(message)s',
        handlers=[StreamHandler(), create_rotating_file_handler(app)]
    )
    patch_threading_excepthook()
    sys.excepthook = handle_unhandled_exception


def create_rotating_file_handler(app):
    return RotatingFileHandler(filename=(OSUtils.get_log_file_path(app)), mode='a',
                               maxBytes=10 * 1024 * 1024, backupCount=2,
                               encoding='utf-8', delay=0)


def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
    """Handler for unhandled exceptions that will write to the logs"""
    if issubclass(exc_type, KeyboardInterrupt):
        # call the default excepthook saved at __excepthook__
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.critical(f'~~~~~~~~~~~~~~~~~~~~~{DateUtil.get_now_in_str("%Y-%m-%d %H:%M:%S")}~~~~~~~~~~~~~~~~~~~~~')
    logging.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))
    logging.critical("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")


def patch_threading_excepthook():
    """Installs our exception handler into the threading modules Thread object
    Inspired by https://bugs.python.org/issue1230540
    """
    old_init = threading.Thread.__init__

    def new_init(self, *args, **kwargs):
        old_init(self, *args, **kwargs)
        old_run = self.run

        def run_with_our_excepthook(*args, **kwargs):
            try:
                old_run(*args, **kwargs)
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                sys.excepthook(*sys.exc_info())

        self.run = run_with_our_excepthook

    threading.Thread.__init__ = new_init
