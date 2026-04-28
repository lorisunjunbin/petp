import json
try:
    import wx
except ImportError:
    wx = None

from core.processor import Processor
from mvp.presenter.event.PETPEvent import PETPEvent


class MATPLOTLIBProcessor(Processor):
    TPL: str = '{"title":"Show MatPlotLib View","chart_type":"PIE|LINE|BAR","top":100,"left":100,"msg":"","show_toolbar":"True","data_json":"{\\"x\\":1,\\"y\\":2}"}'

    DESC: str = f'''
        Send a PETPEvent to launch a Matplotlib chart view in a popup window.
        Supports PIE, LINE, and BAR chart types with configurable position and data.

        - title: Title displayed on the chart window (supports expression, default: "Show MatPlotLib View")
        - chart_type: Type of chart to render, pipe-separated options: PIE|LINE|BAR (supports expression, default: "PIE|LINE|BAR")
        - top: Top position (pixels) of the popup window on screen (supports expression, default: 100)
        - left: Left position (pixels) of the popup window on screen (supports expression, default: 100)
        - msg: Additional message text to display alongside the chart (supports expression, default: "")
        - show_toolbar: If "True", displays the matplotlib toolbar in the popup (supports expression, default: "True")
        - data_json: JSON string providing the chart data, e.g. {{"x":1,"y":2}} (supports expression, default: "{{\"x\":1,\"y\":2}}")

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

        if self.view is not None and wx is not None:
            wx.PostEvent(self.get_view(), PETPEvent(PETPEvent.MATPLOTLIB, {
                "title": title,
                "chart_type": chart_type,
                "msg": msg,
                "top": top,
                "left": left,
                "show_toolbar": show_toolbar,
                "matplotlib_data": data
            }))
        else:
            logging.info(f"[Notification] MATPLOTLIBProcessor: title={title}, chart_type={chart_type}, msg={msg}, top={top}, left={left}, show_toolbar={show_toolbar}, matplotlib_data={data}")
