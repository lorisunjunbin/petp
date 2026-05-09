import logging

from core.processor import Processor
from utils import GlobalCache


class POPULATE_GLOBAL_CACHEProcessor(Processor):
    TPL: str = '{"cache_key":"", "value_key":"", "ttl":""}'

    DESC: str = '''
        Store a value from data_chain into the global cache (in-memory, shared across executions).
        The cached value persists for the process lifetime or until TTL expires.

        - cache_key: cache key to store under (supports expression, required)
        - value_key: data_chain key whose value will be cached (supports expression, required)
        - ttl: time-to-live in seconds; empty means no expiration (supports expression)
    '''

    def get_category(self) -> str:
        return super().CATE_GENERAL

    def process(self):
        super().process()

        cache_key = self.expression2str(self.get_param('cache_key'))
        value_key = self.expression2str(self.get_param('value_key'))

        if not cache_key:
            logging.warning('POPULATE_GLOBAL_CACHE: cache_key is required')
            return

        if not value_key:
            logging.warning('POPULATE_GLOBAL_CACHE: value_key is required')
            return

        value = self.get_data(value_key)

        ttl_str = self.get_param('ttl')
        ttl = None
        if ttl_str:
            ttl_str = self.expression2str(ttl_str).strip()
            if ttl_str:
                ttl = int(ttl_str)

        GlobalCache.set(cache_key, value, ttl)
        logging.info('POPULATE_GLOBAL_CACHE: stored key "%s" (ttl=%s)', cache_key, ttl or 'no expiration')
