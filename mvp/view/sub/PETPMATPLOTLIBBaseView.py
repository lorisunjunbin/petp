import logging

import wx
import matplotlib.figure

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg, NavigationToolbar2WxAgg

"""

	https://matplotlib.org/devdocs/devel/index.html
	https://wiki.wxpython.org/How%20to%20use%20Matplotlib%20-%20Part%201%20%28Phoenix%29

"""


class PETPMATPLOTLIBBaseView(wx.Frame):

	def __init__(self, parent, Id, data):
		super().__init__(parent, Id, title=data['title'])

		logging.info(f'Init {self.__class__.__name__} with data: {data}')

		show_toolbar = True if 'show_toolbar' not in data else data['show_toolbar']
		top = data['top'] if 'top' in data else 100
		left = data['left'] if 'left' in data else 100

		figure = matplotlib.figure.Figure(dpi=self.GetDPI().GetWidth())
		panel = wx.Panel(self)
		axes = figure.add_subplot(111)
		canvas = FigureCanvasWxAgg(panel, -1, figure)

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(canvas, 1, wx.EXPAND)

		if show_toolbar:
			toolbar = NavigationToolbar2WxAgg(canvas)
			toolbar.Realize()
			sizer.Add(toolbar, 0, wx.EXPAND)

		sizer.AddSpacer(self.FromDIP(10))
		panel.SetSizer(sizer)

		self.SetSize(self.FromDIP((1200, 900)))
		self.SetPosition(wx.Point(left, top))
		axes.clear()  # Clear existing plot

		self.update_chart(axes, data['matplotlib_data'])

		canvas.draw()
		canvas.Refresh()
		
	def update_chart(self, axes, data):
		"""
		# Override by sub-class
		:param axes:
		:param data:
		:return:
		"""
		pass
