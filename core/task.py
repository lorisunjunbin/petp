
"""
Task, will be processed by the Processor.
"""

class Task:
    type: str
    input: str

    run_sequence: int
    data_chain: dict

    start: str
    end: str

    def __init__(self, type, input):
        self.type = type
        self.input = input

    def __str__(self):
        return str(self.__dict__)
