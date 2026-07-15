"""
Loop, represent the loop scope and condition.
"""
import json
import logging

class Loop:
    loop_code: str
    loop_attributes: str

    def __init__(self, code, value):
        self.loop_code = code
        self.loop_attributes = value

    @staticmethod
    def tpl():
        # task_start      - task number (1-based row in task grid) where the loop body begins
        # task_end        - task number (1-based row in task grid) where the loop body ends (inclusive)
        # loop_key        - data_chain key whose value is the collection to iterate over;
        #                   mutually exclusive with loop_times (set loop_times to "0" when using loop_key)
        # loop_times      - fixed number of iterations; set to "0" to use loop_key instead
        # loop_index_key  - data_chain key that receives the current 0-based iteration index
        # item_key        - data_chain key that receives the current collection item each iteration
        # exception_then  - behaviour when a task inside the loop raises an exception:
        #                   "break" stops the loop, "continue" skips to the next iteration
        # loop_condition  - optional Python function body (data_chain); evaluated at the end of each iteration:
        #                   return True,'break'    → exit the loop after this iteration
        #                   return True,'continue' → skip to the next iteration immediately
        #                   return False,''        → normal flow, loop continues as before
        return '{"task_start":2, "task_end":5, "loop_key":"loop_list", "loop_times":"0", "loop_index_key":"loop_idx", "item_key":"loop_item", "exception_then":"break", "loop_condition":""}'

    def get_loop_code(self):
        return self.loop_code

    def get_task_start(self):
        return int(self.get_attribute('task_start'))

    def get_task_end(self):
        return int(self.get_attribute('task_end'))

    def get_loop_key(self):
        return self.get_attribute('loop_key')

    def get_loop_times(self):
        return int(self.get_attribute('loop_times'))

    def get_loop_index_key(self):
        return self.get_attribute('loop_index_key')

    def get_item_key(self):
        return self.get_attribute('item_key')

    def get_exception_then(self):
        return self.get_attributes().get('exception_then', '')

    def get_loop_condition(self):
        return self.get_attributes().get('loop_condition', '')

    def get_attribute(self, name):
        return self.get_attributes()[name]

    def is_loop_for_times(self):
        return self.get_loop_times() > 0

    def verify_loop(self):
        if self.get_loop_times() > 0  and len(self.get_loop_key()) > 0:
            err_msg = 'invalid input for loop, loop_times and loop_key can not be used together, give 0 for loop_times if you want to do  collection loop.'
            logging.warning(err_msg)
            raise ValueError(err_msg)

    def get_attributes(self):
        cache = getattr(self, '_attributes_cache', None)
        if cache is None:
            cache = json.loads(self.loop_attributes)
            self._attributes_cache = cache
        return cache

    def __str__(self):
        return str(self.__dict__)
