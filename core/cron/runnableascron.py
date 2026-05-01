from abc import ABC, abstractmethod


class RunnableAsCron(ABC):

    @abstractmethod
    def get_name(self) -> str: ...

    @abstractmethod
    def get_key(self) -> str: ...

    @abstractmethod
    def get_cron(self) -> str: ...

    @abstractmethod
    def run_sync(self, init_param: dict, view, cond) -> None: ...
