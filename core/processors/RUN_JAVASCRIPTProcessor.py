import logging

from core.processor import Processor

_global_cache_js_snippet = {}
_pm = None


class RUN_JAVASCRIPTProcessor(Processor):
	TPL: str = '{"js_file":"", "params":"","data_key":"method_result"}'
	DESC: str = f'''
        Execute a JavaScript function from an external .js file using the PythonMonkey runtime.
        The JS file should export a module with a function that accepts a single argument
        (object/dict) and returns a single result object. The JS snippet is cached globally
        so repeated calls do not re-read the file.

        Requires: pip install pythonmonkey

        - js_file: Path to the JavaScript file to execute (supports expression, default: "")
        - params: Parameters to pass into the JavaScript function; parsed as JSON if applicable (supports expression, default: "")
        - data_key: Key in data_chain to store the JavaScript function's return value (supports expression, default: "method_result")

        {TPL}

    '''

	def get_category(self) -> str:
		return super().CATE_JAVASCRIPT

	def process(self):
		global _pm
		if _pm is None:
			import pythonmonkey
			_pm = pythonmonkey

		js_file = self.expression2str(self.get_param("js_file"))
		data_key = self.expression2str(self.get_param("data_key"))
		params = self.get_json_param("params")

		if js_file not in _global_cache_js_snippet:
			with open(js_file, 'r') as file:
				content = file.read()
				method = _pm.eval(content)
				_global_cache_js_snippet[js_file] = method

		if _global_cache_js_snippet[js_file] is not None:
			result = _global_cache_js_snippet[js_file](params)
			logging.debug(f'RUN_JAVASCRIPTProcessor {data_key} -> {result}')
			self.populate_data(data_key, result)
		else:
			logging.warning(f'RUN_JAVASCRIPTProcessor {js_file} is empty or not found.')
