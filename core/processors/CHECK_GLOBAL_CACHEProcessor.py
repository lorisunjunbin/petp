import logging

from core.processor import Processor
from utils import GlobalCache


class CHECK_GLOBAL_CACHEProcessor(Processor):
    TPL: str = '{"cache_key":"", "data_key":"", "on_hit":"end_execution", "target_task":""}'

    DESC: str = '''
        Check if a value exists in global cache (in-memory, shared across executions).
        On cache hit, binds the cached value to data_chain and optionally controls execution flow.
        On cache miss, does nothing — execution continues to next task.

        - cache_key: cache key to look up (supports expression, required)
        - data_key: key to bind cached value into data_chain (required)
        - on_hit: action on cache hit — "end_execution" / "goto_task" / "continue" (default: "end_execution")
        - target_task: 1-based task number to jump to when on_hit="goto_task" (supports expression)
    '''

    def get_category(self) -> str:
        return super().CATE_GENERAL

    def process(self):
        super().process()

        cache_key = self.expression2str(self.get_param('cache_key'))
        data_key = self.expression2str(self.get_param('data_key'))

        if not cache_key:
            logging.warning('CHECK_GLOBAL_CACHE: cache_key is required')
            return

        value, hit = GlobalCache.get(cache_key)

        if not hit:
            logging.info('CHECK_GLOBAL_CACHE: miss for key "%s"', cache_key)
            return

        logging.info('CHECK_GLOBAL_CACHE: hit for key "%s"', cache_key)
        self.populate_data(data_key, value)

        on_hit = (self.get_param('on_hit') or 'end_execution').strip()

        if on_hit == 'end_execution':
            self.populate_data('__end_execution', True)
        elif on_hit == 'goto_task':
            target = self.expression2str(self.get_param('target_task'))
            if target and target.strip().isdigit():
                self.populate_data('__goto_task', int(target.strip()))
            else:
                logging.warning('CHECK_GLOBAL_CACHE: on_hit=goto_task but target_task is invalid: "%s"', target)
