from random import randint
from typing import Tuple

from service import Service, handler, Message
from ._siowrapper import _SIOWrapper
from .base import BaseCommunicatorKey, BaseCommunicator
from .clients import Clients, ClientInfo
from .comm import SIOKey, ServerSioComm


class CommunicateManager(Service):
    async def warm_up(self):
        self.clients = Clients()

        self.host = "localhost"
        self.port = randint(8100, 10000)

        self._site = _SIOWrapper(self.host, self.port)

        self._site.on("connect", self._on_connect)
        self._site.on("hello", self._on_hello)

        await self._site.run()

    @handler
    async def new_identity(self) -> Tuple[BaseCommunicatorKey, BaseCommunicator]:
        communicator = ServerSioComm(key=None, sio=self._site.sio)
        token = self.clients.new_token(communicator)
        key = SIOKey(host=self.host, port=self.port, token=token)
        return key, communicator

    # SocketIO handlers
    async def _on_connect(self, sid, env):
        self.logger.info("Connected", sid)
        self.clients.connected(sid)

    async def _on_hello(self, sid, data):
        self.logger.info("Hello from", sid)
        client = self.clients.apply_token(sid, data)
        assert isinstance(client, ClientInfo)
        return True

    async def shutdown(self, message: Message):
        await self._site.stop()