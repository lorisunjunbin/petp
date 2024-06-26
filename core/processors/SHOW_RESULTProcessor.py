import logging
import json
import wx

from core.processor import Processor


class SHOW_RESULTProcessor(Processor):
    TPL: str = '{"title":"","msg":""}'

    DESC: str = f''' 
        - To show msg via popup dialog.
        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_GUI

    def process(self):
        title = self.expression2str(self.get_param('title'))
        msg = self.expression2str(self.get_param('msg'))

        logging.info(f'\n\n=========\n{title}\n\n{msg}\n=========\n')
        wx.MessageDialog(None, msg, title).ShowModal()
