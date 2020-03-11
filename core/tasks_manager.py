import asyncio
from typing import List, Any, Tuple

from log import Log


class WrappedCancelledError(Exception):
    pass


class BaseTasksManager:
    def __init__(self, name=""):
        self.logger = Log(f"{self.__class__.__name__}:{name}")
        self._tasks = []
        self._submanagers = []

    async def results(self, return_exceptions=False) -> List[Any]:
        raise NotImplementedError()

    async def pop(self) -> Any:
        raise NotImplementedError()

    @property
    def stats(self) -> List[asyncio.Task, Any]:
        raise NotImplementedError()

    def apply(self, coro, info) -> asyncio.Task:
        raise NotImplementedError()

    def clean(self):
        raise NotImplementedError()

    async def cancel(self):
        raise NotImplementedError()


class TasksManager(BaseTasksManager):
    pass
