"""
Task, will be processed by the Processor.
"""


class Task:
    type: str
    input: str
    skipped: bool

    run_sequence: int
    data_chain: dict

    start: str
    end: str

    def __init__(self, type, input, skipped=False):
        self.type = type
        self.input = input
        self.skipped = skipped

    def __str__(self):
        return str(self.__dict__)
