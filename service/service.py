import asyncio
from asyncio import Queue, CancelledError
from multiprocessing.pool import RemoteTraceback
from typing import TypeVar, Any, Dict, Type, Callable, Awaitable
from concurrent.futures import TimeoutError

from log import Log
from ._background import BackgroundManager
from ._meta import MetaService, HandlersManager
from core import SearchableSubclasses
from .error import UnknownMessageType, ServiceExist
from .message import Message, Shutdown


_TM = TypeVar("_TM", Message, Message)


class Service(BackgroundManager, SearchableSubclasses, metaclass=MetaService):
    logger = Log(f"ServiceClass:{__name__}")

    cpu_bound = False
    _instance: "Service" = None
    _handlers: Dict[Type[Message], Callable[[Message], Awaitable[Any]]]
    _handlers_manager: HandlersManager = None

    main_queue: asyncio.Queue = None

    def __init__(self, message: Message):
        if self.__class__._instance:
            raise ServiceExist(self.__class__._instance)

        self.__class__._instance = self

        self.logger = Log(f"Service:{self.__class__.__name__}")
        self._queue: Queue[Message] = Queue()

        super().__init__()
        self.logger.info("🖥 Hello!")

    async def warm_up(self):
        """
        Метод запускается перед запуском основного цикла программы.
        Здесь можно подготовить сервис к работе
        """
        pass

    async def process(self, message: Message):
        """
        Позволяет обрабатывать сообщения в общем виде
        Если метод возвращает None -- считается, что метод ничего не обработал
        """
        pass

    async def shutdown(self, message: Message):
        """
        Здесь можно отключить вспомогательные механизмы сервиса
        """
        pass

    async def run(self):
        """
        Точка входа для сервиса
        :return:
        """
        _shutdown_msg = None

        try:
            self.logger.info("🔥 Warming up")
            await self.warm_up()

            while True:
                await self._collect_aio_tasks()

                try:
                    msg = await asyncio.wait_for(self._queue.get(), 2)
                except TimeoutError:
                    continue

                self.logger.info("💌", message=msg)

                if isinstance(msg, Shutdown) and msg.to is self.__class__:
                    _shutdown_msg = msg
                    break

                custom_processor = self._found_processor(msg)

                self._run_background(
                    self._apply_task(msg, custom_processor)
                )

        except CancelledError:
            self.logger.info("⏹ Service cancelled")
        except RemoteTraceback:
            raise
        except Exception as e:
            self.logger.exception()
            raise
        finally:
            await self._stop_aio_tasks()
            self.logger.info("💀 Shutdown")
            if not _shutdown_msg:
                _shutdown_msg = Shutdown(cause="Cancelled")

            shutdown_result = await self.shutdown(_shutdown_msg)
            _shutdown_msg.set_result(shutdown_result)

        self.logger.info("👋 Bye!")

    def _found_processor(self, msg):
        custom_processor = self.process
        if type(msg) in self._handlers:
            custom_processor = self._handlers[type(msg)]
            self.logger.debug("Found custom processor", processor=custom_processor)
        return custom_processor

    async def _apply_task(self,
                          message: Message,
                          method: Callable[[Message], Awaitable[Any]]):
        try:
            result = await method(message)
            if method == self.process and result is None:
                raise UnknownMessageType(self, message)

            message.set_result(result)
        except RemoteTraceback:
            raise
        except Exception as e:
            self.logger.exception(message=message)
            message.set_error(e)

    @classmethod
    async def send(cls, message: _TM) -> _TM:
        """
        Позволяет отправить в сервис сообщение
        """
        message.to = cls
        await cls.main_queue.put(message)
        return message

    @classmethod
    async def get(cls, message: Message) -> Any:
        """
        Позволяет получить результат вычислений
        """
        msg = await cls.send(message)
        return await msg.result()

    def __repr__(self):
        return f"<Service:{self.__class__.__name__}: [{self._queue.qsize()}] / [{len(self._aio_tasks)}]>"

    @classmethod
    async def cleanup(cls):
        """ Восстановление первоначального состояния """
        cls._instance = None

        if cls is Service:
            cls._main_queue : asyncio.Queue
            while not cls._main_queue.empty():
                item = await cls._main_queue.get()
                cls.logger.warning("Orphan message from the main queue:", msg=item)

            cls._main_queue = None
