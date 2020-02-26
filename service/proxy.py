from typing import Type

from service import Service, handler, Message
from .communicator import BaseCommunicator


class ProcessSpawner(Service):
    @handler
    async def create_process(self, service_class: Type[Service]):
        raise NotImplementedError()


class ProxyInit(Message):
    def __init__(self, communicator: BaseCommunicator):
        super().__init__()
        self.communicator = communicator


class ProxyClient(Service):
    def __init__(self, message: ProxyInit):
        super().__init__(message)
        self.communicator = message.communicator

    async def warm_up(self):
        await self.communicator.run(quiet=True)
        self._run_background(self._msg_receiver())

    async def _msg_receiver(self):
        while True:
            msg = await self.communicator.receive_msg()
            await self.main_queue.put(msg)

    async def _found_processor(self, msg: Message):
        return self.communicator.send_msg


class ProxyServer(ProxyClient):
    pass
