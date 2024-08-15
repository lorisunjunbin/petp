from mvp.view.sub.PETPMATPLOTLIBBaseView import PETPMATPLOTLIBBaseView

class PETP_BAR_CHARTView(PETPMATPLOTLIBBaseView):
	"""
	{
	  "species": ["apple", "blueberry", "cherry", "orange"],
	  "counts": [40, 100, 30, 66],
	  "bar_labels": ["red", "blue", "_red", "orange"],
	  "bar_colors": ["tab:red", "tab:blue", "tab:red", "tab:orange"],
	  "x_label": "Fruit Kind",
	  "y_label": "Fruit supply",
	  "bar_title": "Fruit supply by kind and color",
	  "legend_title": "Fruit color"
	}
	"""

	def update_chart(self, axes, data):
		species = data['species'] if 'species' in data else []
		counts = data['counts'] if 'counts' in data else []
		bar_labels = data['bar_labels'] if 'bar_labels' in data else []
		bar_colors = data['bar_colors'] if 'bar_colors' in data else []

		axes.bar(species, counts, label=bar_labels, color=bar_colors)

		axes.set_xlabel(data['x_label'] if 'x_label' in data else 'x_label')
		axes.set_ylabel(data['y_label'] if 'y_label' in data else 'y_label')
		axes.set_title(data['bar_title'] if 'bar_title' in data else 'bar_title')
		axes.legend(title=data['legend_title'] if 'legend_title' in data else 'legend_title')
