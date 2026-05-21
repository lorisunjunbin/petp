try:
    import wx
except ImportError:
    wx = None
from threading import Thread
from threading import Condition
from mvp.presenter.event.PETPEvent import PETPEvent


class Executor(Thread):
    """
    Executor class that extends Thread. This class is responsible for executing execution in a new thread.
    """

    def __init__(self, execution, init_data, wx_comp):
        self.condition = Condition()
        self.execution = execution
        self.wx_comp = wx_comp
        self.init_data = init_data
        super().__init__(daemon=True, args=(self.condition,))

    def run(self):
        if wx is not None and self.wx_comp is not None:
            wx.PostEvent(self.wx_comp, PETPEvent(PETPEvent.START, [self.execution.execution, self.init_data]))
        error = None
        error_context = None
        try:
            data_chain = self.execution.run(self.init_data, self.condition, self.wx_comp)
        except Exception as e:
            import logging
            import traceback as tb
            logging.exception('Executor caught unhandled exception in %s', self.execution.execution)
            data_chain = self.init_data
            self._cleanup_chrome_drivers(data_chain)
            error = str(e)
            task_index = -1
            task_type = ''
            task_input = ''
            if hasattr(self.execution, 'state') and self.execution.state:
                task_index = self.execution.state.get_current_index()
            if task_index >= 0 and task_index < len(self.execution.list):
                failed_task = self.execution.list[task_index]
                task_type = failed_task.type
                task_input = getattr(failed_task, 'input', '')
            error_context = {
                'error': error,
                'traceback': tb.format_exc(),
                'task_index': task_index,
                'task_type': task_type,
                'task_input': task_input,
                'execution_name': self.execution.execution,
            }
        if wx is not None and self.wx_comp is not None:
            wx.PostEvent(self.wx_comp, PETPEvent(PETPEvent.DONE, [self.execution.execution, data_chain, error, error_context]))

    @staticmethod
    def _cleanup_chrome_drivers(data_chain) -> None:
        """Best-effort quit of any selenium driver leaked into data_chain on the
        exception path — without it, a Chrome process survives the failed run and
        accumulates over time in long-running BG/Docker deployments."""
        if not isinstance(data_chain, dict):
            return
        import logging
        for k, v in list(data_chain.items()):
            cls = getattr(v, '__class__', None)
            if cls is None:
                continue
            module_name = str(getattr(cls, '__module__', '')).lower()
            class_name = str(getattr(cls, '__name__', '')).lower()
            if not ('selenium' in module_name and 'webdriver' in module_name and 'chrome' in (module_name + class_name)):
                continue
            try:
                v.quit()
                logging.info('cleaned up leaked chrome driver at data_chain[%r]', k)
            except Exception as e:
                logging.warning('chrome driver cleanup failed for %r: %s', k, e)
