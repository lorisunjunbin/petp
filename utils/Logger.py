import logging
import sys
import threading

from utils.DateUtil import DateUtil
from utils.ExcelUtil import ExcelUtil


def init(app):

    fmt = '<%(levelname)s>[ %(threadName)s ] - %(message)s'

    logging.basicConfig(
        filename=ExcelUtil.get_log_file_path(app),
        level=logging.INFO,
        encoding='utf-8',
        datefmt='%m/%d/%Y %I:%M:%S',
        format=fmt
    )

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(fmt))
    logging.getLogger('').addHandler(console)

    patch_threading_excepthook()
    sys.excepthook = handle_unhandled_exception

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

