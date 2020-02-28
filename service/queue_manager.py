import asyncio
from typing import Dict, Type, Callable, Any, Awaitable, Sequence

from core import Attribute
from service import Service, Message, handler


class QueueManagerInit(Message):
    instances: Sequence[Service] = Attribute()


class QueueManager(Service):
    def __init__(self, message: QueueManagerInit):
        super().__init__(message)
        self._queue = self.__class__.main_queue
        self._queues: Dict[Type[Service], asyncio.Queue] = {
            self.__class__: self._queue
        }

        for instance in message.instances:
            self._register(instance)

    async def process(self, message: Message):
        assert message.to
        if message.to not in self._queues:
            from service import ServiceRunner
            msg = await ServiceRunner.create_service(message.to)
            instance = await msg.result()
            queue = instance._queue
        else:
            queue = self._queues[message.to]
        await queue.put(message)

    async def _apply_task(self,
                          message: Message,
                          method: Callable[[Message], Awaitable[Any]]):
        try:
            result = await method(message)
            if method == self.process and result is None:
                # self.process just put message into correct queue
                return

            message.set_result(result)
        except Exception as e:
            self.logger.exception(message=message)
            message.set_error(e)

    @handler
    async def register(self, instance: Service):
        return self._register(instance)

    def _register(self, instance: Service):
        self._queues[instance.__class__] = instance._queue
        return True
