import numpy as np

from mvp.view.sub.PETPMATPLOTLIBBaseView import PETPMATPLOTLIBBaseView

"""

	https://wiki.wxpython.org/How%20to%20use%20Matplotlib%20-%20Part%201%20%28Phoenix%29

"""


class PETP_PIE_CHARTView(PETPMATPLOTLIBBaseView):

	def update_chart(self, axes, data):
		"""
		{
		  "labels": ["Hogs", "Frogs", "Logs", "Dogs"],
		  "sizes": [15, 40, 60, 5],
		  "explode": [0, 0, 0.1, 0],
		  "text_size": "larger",
		  "shadow": false,
		  "radius": 0.9
		}
		"""

		# labels = ['Hogs', 'Frogs', 'Logs', 'Dogs']
		labels = data['labels'] if 'labels' in data else ['label1', 'label2', 'label3', 'label4']

		# sizes = [15, 30, 45, 10]
		sizes = data['sizes'] if 'sizes' in data else [15, 40, 60, 5]

		# explode = [0, 0, 0.1, 0]
		explode = data['explode'] if 'explode' in data else [0, 0, 0.1, 0]

		axes.pie(sizes,
				 labels=labels,
				 autopct='%1.1f%%',
				 textprops={'size': data['text_size'] if 'text_size' in data else 'smaller'},
				 shadow=data['shadow'] if 'shadow' in data else True,
				 radius=data['radius'] if 'radius' in data else 1.1,
				 startangle=90,
				 explode=explode)
