import asyncio
from asyncio import Queue, Task
from typing import List, TypeVar, Type, Any

from log import Log
from .message import Message, Shutdown


_TM = TypeVar("M", Message, Message)


class Service:
    _instance: "Service" = None

    def __init__(self, message: Message):
        if self.__class__._instance:
            raise RuntimeError("Service already exist")

        self.__class__._instance = self

        self.logger = Log(f"Service:{self.__class__.__name__}")
        self._queue: Queue[Message] = Queue()
        self._aio_tasks: List[Task] = []
        self.logger.info("Hello!")

    async def warm_up(self):
        pass

    async def process(self, message: Message):
        pass

    async def shutdown(self, message: Message):
        pass

    async def run(self):
        self.logger.info("Warming up")
        await self.warm_up()

        while True:
            await self._collect_tasks()

            msg = await self._queue.get()
            self.logger.info(message=msg)

            if isinstance(msg, Shutdown):
                self.logger.info("Shutdown")
                msg.set_result(await self.shutdown(msg))
                break

            new_task = asyncio.create_task(self._apply_task(msg))
            self._aio_tasks.append(new_task)

        self.logger.info("Bye!")

    async def _collect_tasks(self):
        to_delete = tuple(task for task in self._aio_tasks if task.done())

        if to_delete:
            self.logger.debug("Collect tasks", coutn=len(to_delete))

        for task in to_delete:
            self._aio_tasks.remove(task)

    async def _apply_task(self, message: Message):
        try:
            message.set_result(await self.process(message))
        except Exception as e:
            self.logger.exception(message=message)
            message.set_error(e)

    @classmethod
    async def send(cls, message: _TM) -> _TM:
        from service import ServiceRunner
        instance: cls = await ServiceRunner.get_instance(cls)
        await instance._queue.put(message)
        message.to = cls
        return message

    @classmethod
    async def get(cls, message: Message) -> Any:
        msg = await cls.send(message)
        return await msg.result()

    @classmethod
    def search(cls, name: str) -> Type['Service']:
        for klass in Service.__subclasses__():
            klass: Type[Service]
            if klass.__name__ == name:
                return klass

        raise NameError(f"Not found service with name {name}. "
                        f"Class must be subclass of `Service`",
                        name, tuple(klass.__name__ for klass in Service.__subclasses__()))
