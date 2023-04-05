import logging

import wx

from core.processor import Processor


class INPUT_DIALOGProcessor(Processor):
    TPL: str = '{"title":" Message Input","msg":"","value_key":"","default_value":""}'

    DESC: str = f''' 
        DOES NOT WORKS, due to run execution in a new thread, try to figure out later.
        To collect user input via popup text entry dialog, save to data_chain. wx must run Dialog in MainThread, so should not use this processor as cron mode. 
        
        {TPL}
        
    '''

    def process(self):
        title = self.expression2str(self.get_param('title'))
        msg = self.expression2str(self.get_param('msg'))
        value_key = self.expression2str(self.get_param('value_key'))
        default_value = self.expression2str(self.get_param('default_value')) if self.has_param('default_value') else ''

        dlg = wx.TextEntryDialog(None, msg, title)
        dlg.SetValue(default_value)
        if dlg.ShowModal() == wx.ID_OK:
            self.populate_data(value_key, dlg.GetValue())
        dlg.Destroy()
        logging.info(f'\n\n=========\n{self.get_data(value_key)}\n=========\n')
