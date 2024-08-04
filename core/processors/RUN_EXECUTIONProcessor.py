import logging

import wx

from core.processor import Processor
from mvp.presenter.event.PETPEvent import PETPEvent


class RUN_EXECUTIONProcessor(Processor):
	TPL: str = '{"execution":"EXECUTION_NAME", "params":"","if_stop":"no"}'
	DESC: str = f'''
        - Run a specific execution with params. if_stop is set to yes, the execution will be skipped.

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

			wx.PostEvent(self.get_view(), PETPEvent(PETPEvent.HTTP_CALLBACK, {
				"action": "execution",
				"params": params
			}))
		else:
			logging.debug(f'RUN_EXECUTIONProcessor - skipped')
