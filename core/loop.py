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
        # task_start / task_end - task number in task grid
        # loop_key - attribute of the data_chain which represent data collection
        # item_key - attribute of the data_chain which represent item of data collection that pass into the loop tasks.
        # loop_index - loop cursor
        # loop_times - attribute of the data_chain which represent loop times, use this, must remove attribute loop_key
        return '{"task_start":2, "task_end":5, "loop_key":"loop_list", "loop_times":"0", "loop_index_key":"loop_idx", "item_key":"loop_item"}'

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
        return json.loads(self.loop_attributes)

    def __str__(self):
        return str(self.__dict__)
