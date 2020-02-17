import asyncio
from asyncio import Queue
from typing import Dict, Type, List

from log import Log
from .error import ServiceStartError, ServiceSearchError
from .task import ShutdownTask, Task


class Service:
    services: Dict[Type['Service'], 'Service'] = {}

    def __init__(self, task: Task = None):
        if self.__class__ in self.services:
            raise ServiceStartError(self.__class__, "already started")

        self.logger = Log(self.__class__.__name__)
        self.queue: Queue[Task] = Queue()

        self.services[self.__class__] = self
        self._aio_tasks: List[asyncio.Task] = []

    async def warm_up(self):
        pass

    async def run(self):
        # TODO: Add Exception
        self.logger.info("Warming up")
        await self.warm_up()

        while True:
            task = await self.queue.get()
            self.logger.debug(task=task)

            if isinstance(task, ShutdownTask):
                break

            self._aio_tasks.append(
                asyncio.create_task(self._apply_task(task))
            )

            await self._collect_tasks()

        self.logger.info("Shutting down by", task=task)
        await task.set_result(await self.shutdown(task))

        self.logger.info("Bye!")

        del self.services[self.__class__]

    async def _apply_task(self, task):
        await task.set_result(await self.process(task))

    async def process(self, task: Task):
        pass

    async def shutdown(self, task: Task):
        pass

    async def _collect_tasks(self):
        done_tasks = tuple(task for task in self._aio_tasks if task.done())
        if done_tasks:
            self.logger.deep_debug("Cleanup tasks", count=len(done_tasks))

        for task in done_tasks:
            self._aio_tasks.remove(task)
            del task

    @classmethod
    async def send_task(cls, task):
        # TODO: Use QueueService
        if cls not in cls.services:
            await cls._do_run_service(cls)
        instance = cls.services[cls]
        await instance.queue.put(task)
        return task

    @classmethod
    async def _do_run_service(cls, klass: Type['Service']):
        from service.runner import ServiceRunner

        from service.runner import RunService
        task = await ServiceRunner.send_task(RunService(klass))

        assert cls.services[cls] is task.result()

    @classmethod
    def search(cls, name):
        for klass in Service.__subclasses__():
            if klass.__name__ == name:
                return klass

        raise ServiceSearchError(name,
                                 [klass.__name__ for klass in cls.__subclasses__()])
