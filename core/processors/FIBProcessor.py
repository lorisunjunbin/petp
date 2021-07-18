import logging

from functools import cache

from core.processor import Processor


class FIBProcessor(Processor):
    TPL: str = '{"seed":"","useCache":"yes|no"}'

    DESC: str = f'''
        This is task run fib calculate.
        {TPL}
    '''

    def process(self):
        seed: int = int(self.get_param('seed'))
        use_cache = True if "yes" == self.get_param('useCache') else False
        if use_cache: 
            for i in range(seed):
                logging.info(f"{i} -> {self.fib(i)}")    
        else:
            for i in range(seed):
                logging.info(f"{i} -> {self.fib_slow(i)}")    
                
        logging.info('DONE')   
        
    
    @cache    
    def fib (self, n):
        if n <=1:
            return n
        return self.fib(n-1) + self.fib(n-2)    
        
    
    def fib_slow (self, n):
        if n <=1:
            return n
        return self.fib_slow(n-1) + self.fib_slow(n-2)    