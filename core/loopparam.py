from core.loop import Loop


class LoopParam:

    def __init__(self, l: list):

        self.list_size = len(l)
        self.current_loop = None

        # loop for collection
        self.current_loop_collection: []
        self.current_loop_idx = 0

        # loop for times
        self.loop_times = 0
        self.loop_times_cur = 0

        # loop index
        self.current_index = 0

        self.is_loop_execution = None
        self.is_times_loop = None
        self.is_loop_start = None
        self.is_loop_end = None

    def setup_loop_end(self, data_chain: dict):
        if self.is_times_loop:
            self.loop_times_cur += 1
            if self.loop_times > self.loop_times_cur:
                self.current_index = self.current_loop.get_task_start() - 1
                data_chain[self.current_loop.get_loop_index_key()] = self.loop_times_cur
            else:
                self.loop_times_cur = 0
                self.loop_times = 0
                data_chain[self.current_loop.get_loop_index_key()] = 0
        else:
            self.current_loop_idx += 1
            if len(self.current_loop_collection) > self.current_loop_idx:
                self.current_index = self.current_loop.get_task_start() - 1
                data_chain[self.current_loop.get_loop_index_key()] = self.current_loop_idx
            else:
                self.current_loop_idx = 0
                data_chain[self.current_loop.get_item_key()] = None
                data_chain[self.current_loop.get_loop_index_key()] = 0

    def setup_loop_start(self, data_chain: dict):
        if self.is_times_loop:
            self.loop_times = self.current_loop.get_loop_times()
            data_chain[self.current_loop.get_loop_index_key()] = self.loop_times_cur
        else:
            self.current_loop_collection = data_chain[self.current_loop.get_loop_key()]
            if len(self.current_loop_collection) > self.current_loop_idx:
                data_chain[self.current_loop.get_item_key()] = self.current_loop_collection[self.current_loop_idx]
                data_chain[self.current_loop.get_loop_index_key()] = self.current_loop_idx

    def init_loop(self, current_loop: Loop):
        self.current_loop = current_loop
        self.is_loop_execution = current_loop is not None
        self.is_times_loop = self.is_loop_execution and current_loop.is_loop_for_times()
        self.is_loop_start = self.is_loop_execution and self.get_sequence() == current_loop.get_task_start()
        self.is_loop_end = self.is_loop_execution and self.get_sequence() == current_loop.get_task_end()

    def has_next(self):
        return self.current_index < self.list_size

    def move_to_next(self):
        self.current_index += 1

    def get_sequence(self) -> int:
        return self.current_index + 1

    def __str__(self):
        return str(self.__dict__)
