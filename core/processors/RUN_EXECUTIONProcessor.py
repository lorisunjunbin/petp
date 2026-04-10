import logging

try:
    import wx
except ImportError:
    wx = None

from core.processor import Processor
from mvp.presenter.event.PETPEvent import PETPEvent


class RUN_EXECUTIONProcessor(Processor):
    TPL: str = '{"execution":"EXECUTION_NAME", "params":"","if_stop":"no"}'
    DESC: str = f'''
        Run (trigger) a specific execution by name with optional parameters. If if_stop is set to "yes", the execution will be skipped entirely.

        - execution: The name of the execution to run (supports expression, default: "EXECUTION_NAME")
        - params: Additional parameters to pass to the execution as a JSON string (supports expression, default: "")
        - if_stop: If "yes", skip running this execution; if "no", proceed normally (supports expression, default: "no")

        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_GENERAL

    def process(self):

        run: bool = False if "yes" == self.expression2str(self.get_param("if_stop")) else True

        if run:
            execution = self.expression2str(self.get_param("execution"))
            params = self.json2dict(self.expression2str(self.get_param("params")))
            params["execution"] = execution

            logging.debug(f'RUN_EXECUTIONProcessor - {execution} - {params}')

            if wx is not None:
                wx.PostEvent(self.get_view(), PETPEvent(PETPEvent.HTTP_REQUEST, {
                    "action": "execution",
                    "params": params
                }))
            else:
                logging.info(f"[Notification] RUN_EXECUTIONProcessor: execution={execution}, params={params}")
