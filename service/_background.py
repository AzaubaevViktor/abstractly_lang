import asyncio
from asyncio.tasks import Task
from typing import List, Coroutine

from log import Log


class BackgroundManager:
    def __init__(self):
        self._logger = Log(f"{self.__class__.__name__}:BackgroundManager")
        self._aio_tasks: List[Task] = []

    def _run_background(self, coro: Coroutine):
        self._aio_tasks.append(
            asyncio.create_task(coro)
        )

    async def _collect_aio_tasks(self):
        to_delete = tuple(task for task in self._aio_tasks if task.done())

        if to_delete:
            self._logger.debug("🗑 Collect tasks", count=len(to_delete))

        for task in to_delete:
            self._aio_tasks.remove(task)

    async def _stop_aio_tasks(self):
        if self._aio_tasks:
            self._logger.info("☠️ Cancel tasks", count=len(self._aio_tasks))
            for task in self._aio_tasks:
                task.cancel()
                await task