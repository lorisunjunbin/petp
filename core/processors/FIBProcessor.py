import logging

from functools import cache

from core.processor import Processor


class FIBProcessor(Processor):
	TPL: str = '{"seed":"","useCache":"yes|no","data_key":"fib_arr"}'

	DESC: str = f'''
        This is task run fib calculate.
        {TPL}
    '''

	def get_category(self) -> str:
		return super().CATE_DATA_PROCESSING

	def process(self):
		seed: int = int(self.get_data('seed')) if self.has_data('seed') else int(self.get_param('seed'))
		data_key: str = self.get_param('data_key')
		use_cache = True if "yes" == self.get_param('useCache') else False
		data = []

		if use_cache:
			for i in range(seed):
				msg = f"{i} -> {self.fib(i)}"
				logging.info(msg)
				data.append(msg)
		else:
			for i in range(seed):
				msg = f"{i} -> {self.fib_slow(i)}"
				logging.info(msg)
				data.append(msg)

		self.populate_data(data_key, data)

	@cache
	def fib(self, n):
		if n <= 1:
			return n
		return self.fib(n - 1) + self.fib(n - 2)

	def fib_slow(self, n):
		if n <= 1:
			return n
		return self.fib_slow(n - 1) + self.fib_slow(n - 2)
