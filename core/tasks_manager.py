import asyncio
from asyncio import CancelledError
from typing import List, Any, Tuple, Dict, Sequence, ItemsView

from log import Log


class BaseTasksManager:
    def __init__(self, name=""):
        self.logger = Log(f"{self.__class__.__name__}:{name}")
        self._tasks: Dict[asyncio.Task, Any] = {}

    def run(self, *coros) -> Sequence[asyncio.Task]:
        tasks = []
        for coro_ in coros:
            tasks.append(self.apply(coro_, None))

        return tuple(tasks)

    def apply(self, coro, info: Any) -> asyncio.Task:
        task = asyncio.create_task(coro)
        self._tasks[task] = info
        return task

    @property
    def stats(self) -> ItemsView[asyncio.Task, Any]:
        return self._tasks.items()

    async def pop(self, sleep_=0.1) -> Any:
        task_done = None
        while task_done is None:
            for task in self._tasks:
                if task.done():
                    task_done = task
                    break

            if task_done is None:
                await asyncio.sleep(sleep_)

        del self._tasks[task_done]

        return await task_done

    async def results(self, return_exceptions=False) -> List[Any]:
        results = []
        for task in self._tasks:
            try:
                results.append(await task)
            except Exception as e:
                if return_exceptions:
                    results.append(e)
                else:
                    raise

        self._tasks.clear()

        return results

    async def clean(self) -> int:
        to_remove = []

        try:
            for task in self._tasks:
                if task.done():
                    to_remove.append(task)

                    await task
        except Exception:
            raise
        finally:
            for task in to_remove:
                del self._tasks[task]

        return len(to_remove)

    async def cancel(self):
        if self._tasks:
            self.logger.debug("☠️ Cancel tasks", count=len(self._tasks))
            for task in self._tasks.keys():
                task.cancel()
                try:
                    await task
                except CancelledError:
                    pass
                except Exception:
                    self.logger.exception("While cancel task")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print(exc_type, exc_val, exc_tb)
        await self.cancel()


class TasksManager(BaseTasksManager):
    pass
