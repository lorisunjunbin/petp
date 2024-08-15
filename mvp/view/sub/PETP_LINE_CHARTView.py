from mvp.view.sub.PETPMATPLOTLIBBaseView import PETPMATPLOTLIBBaseView


class PETP_LINE_CHARTView(PETPMATPLOTLIBBaseView):
	"""
	{
		"categories":{
			"Categorical": {"202408": 10, "202409": 15, "202410": 5, "202411": 23},
			"Plotting": {"202408": 10, "202409": 25, "202410": 14, "202411": 23}
		},
		"title": "Line chart",
		"x_label": "Months",
		"y_label": "Count",
		"legend_loc": "upper right"
	}
	"""

	def update_chart(self, axes, data):
		categories = data['categories'] if 'categories' in data else {
			"Categorical": {'202408': 10, '202409': 15, '202410': 5, '202411': 23},
			"Plotting": {'202408': 10, '202409': 25, '202410': 14, '202411': 23}
		}

		for key, val in categories.items():
			axes.plot(list(val.keys()), list(val.values()), label=key)

		axes.set_title(data['title'] if 'title' in data else 'Line Chart Title')
		axes.set_xlabel(data['x_label'] if 'x_label' in data else 'x_label')
		axes.set_ylabel(data['y_label'] if 'y_label' in data else 'y_label')
		axes.axhline(0, color='black', linewidth=0.5)
		axes.axvline(0, color='black', linewidth=0.5)
		axes.grid(color='gray', linestyle='--', linewidth=0.5)
		axes.legend(loc=data['legend_loc'] if 'legend_loc' in data else 'upper right')
