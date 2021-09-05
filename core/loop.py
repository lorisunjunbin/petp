"""
Loop, represent the loop scope and condition.
"""
import json


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
        return '{"task_start":2, "task_end":5, "loop_key":"loop_list","loop_index_key":"loop_idx", "item_key":"loop_item"}'

    def get_loop_code(self):
        return self.loop_code

    def get_task_start(self):
        return int(self.get_attribute('task_start'))

    def get_task_end(self):
        return int(self.get_attribute('task_end'))

    def get_loop_key(self):
        return self.get_attribute('loop_key')

    def get_loop_index_key(self):
        return self.get_attribute('loop_index_key')

    def get_item_key(self):
        return self.get_attribute('item_key')

    def get_attribute(self, name):
        return self.get_attributes()[name]

    def get_attributes(self):
        return json.loads(self.loop_attributes)

    def __str__(self):
        return str(self.__dict__)
