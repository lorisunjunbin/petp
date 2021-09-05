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
        return '{"task_start":2, "task_end":5, "loop_key":"list", "item_key":"item"}'

    def get_attribute(self, name):
        return self.get_attributes()[name]

    def get_attributes(self):
        return json.loads(self.loop_attributes)

    def __str__(self):
        return str(self.__dict__)
