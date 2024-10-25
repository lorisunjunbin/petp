import json
import wx

from core.processor import Processor
from mvp.presenter.event.PETPEvent import PETPEvent


class MATPLOTLIBProcessor(Processor):
	TPL: str = '{"title":"Show MatPlotLib View","chart_type":"PIE|LINE|BAR","top":100,"left":100,"msg":"","show_toolbar":"True","data_json":"{\\"x\\":1,\\"y\\":2}"}'

	DESC: str = f''' 
        - To send PETPEvent to launch Matplotlib view in a popup window.
        
        {TPL}
    '''

	def get_category(self) -> str:
		return super().CATE_GUI

	def process(self):
		title = self.expression2str(self.get_param('title'))
		chart_type = self.expression2str(self.get_param('chart_type'))
		msg = self.expression2str(self.get_param('msg'))
		left = int(self.expression2str(self.get_param('left'))) if self.has_param('left') else 100
		top = int(self.expression2str(self.get_param('top'))) if self.has_param('top') else 200

		show_toolbar = True if 'True' == self.expression2str(self.get_param('show_toolbar')) else False
		data = self.get_json_param('data_json')

		wx.PostEvent(self.get_view(), PETPEvent(PETPEvent.MATPLOTLIB, {
			"title": title,
			"chart_type": chart_type,
			"msg": msg,
			"top": top,
			"left": left,
			"show_toolbar": show_toolbar,
			"matplotlib_data": data
		}))
