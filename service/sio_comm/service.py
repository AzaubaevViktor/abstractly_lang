from random import randint
from typing import Tuple

from service import Service, handler, Message
from ._siowrapper import _SIOWrapper
from .base import BaseCommunicatorKey, BaseCommunicator
from ._clients import _Clients
from .comm import SIOKey, ServerSioComm


class CommunicateManager(Service):
    async def warm_up(self):
        self.clients = _Clients()

        self.host = 'localhost'
        self.port = randint(8100, 10000)

        self._site = _SIOWrapper(self.host, self.port)
        await self._site.run()

    @handler
    async def new_identity(self) -> Tuple[BaseCommunicatorKey, BaseCommunicator]:
        token = self.clients.new_token()
        key = SIOKey(host=self.host, port=self.port, token=token)
        communicator = ServerSioComm(key=None, sio=self._site.sio)
        return key, communicator

    async def shutdown(self, message: Message):
        await self._site.stop()