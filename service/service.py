import asyncio
from asyncio import Queue, Task, CancelledError
from typing import List, TypeVar, Any, Dict, Type, Callable, Awaitable

from log import Log
from ._meta import MetaService, HandlersManager
from ._searchable import SearchableSubclasses
from .message import Message, Shutdown


_TM = TypeVar("_TM", Message, Message)


class Service(SearchableSubclasses, metaclass=MetaService):
    _instance: "Service" = None
    _handlers: Dict[Type[Message], Callable[[Message], Awaitable[Any]]]
    _handlers_manager: HandlersManager = None

    def __init__(self, message: Message):
        if self.__class__._instance:
            raise RuntimeError("⛔️ Service already exist")

        self.__class__._instance = self

        self.logger = Log(f"Service:{self.__class__.__name__}")
        self._queue: Queue[Message] = Queue()
        self._aio_tasks: List[Task] = []
        self.logger.info("🖥 Hello!")

    async def warm_up(self):
        pass

    async def process(self, message: Message):
        pass

    async def shutdown(self, message: Message):
        pass

    async def run(self):
        _shutdown_msg = None

        try:
            self.logger.info("🔥 Warming up")
            await self.warm_up()

            while True:
                await self._collect_aio_tasks()

                msg = await self._queue.get()
                self.logger.info("💌", message=msg)

                if isinstance(msg, Shutdown):
                    _shutdown_msg = msg
                    break

                custom_processor = self._found_processor(msg)

                new_task = asyncio.create_task(self._apply_task(msg, custom_processor))
                self._aio_tasks.append(new_task)

        except CancelledError:
            self.logger.info("⏹ Service cancelled")
        finally:
            await self._stop_aio_tasks()
            self.logger.info("💀 Shutdown")
            if not _shutdown_msg:
                _shutdown_msg = Shutdown("Cancelled")

            shutdown_result = await self.shutdown(_shutdown_msg)
            _shutdown_msg.set_result(shutdown_result)

        self.logger.info("👋 Bye!")

    def _found_processor(self, msg):
        custom_processor = self.process
        if type(msg) in self._handlers:
            custom_processor = self._handlers[type(msg)]
            self.logger.debug("Found custom processor", processor=custom_processor)
        return custom_processor

    async def _collect_aio_tasks(self):
        to_delete = tuple(task for task in self._aio_tasks if task.done())

        if to_delete:
            self.logger.debug("🗑 Collect tasks", count=len(to_delete))

        for task in to_delete:
            self._aio_tasks.remove(task)

    async def _stop_aio_tasks(self):
        if self._aio_tasks:
            self.logger.info("☠️ Cancel tasks", count=len(self._aio_tasks))
            for task in self._aio_tasks:
                task.cancel()
                await task

    async def _apply_task(self,
                          message: Message,
                          method: Callable[[Message], Awaitable[Any]]):
        try:
            message.set_result(await method(message))
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

    def __repr__(self):
        return f"<Service:{self.__class__.__name__}: [{self._queue.qsize()}] / [{len(self._aio_tasks)}]>"
