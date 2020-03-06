from typing import TypeVar, Tuple

from service import Message, Service, handler
from ._site import _Site

_MsgT = TypeVar("_MsgT", Message, Message)


class BaseCommunicatorKey(object):
    pass


class BaseCommunicator:
    def __init__(self, key: BaseCommunicatorKey):
        self.key = key

    async def connect(self):
        raise NotImplementedError()

    @property
    def connected(self):
        raise NotImplementedError()

    async def send(self, msg: _MsgT) -> _MsgT:
        msg: Message
        raise NotImplementedError()

    async def get(self, msg: Message):
        msg = await self.send(msg)
        return await msg.result()

    async def recv(self) -> Message:
        raise NotImplementedError()

    async def disconnect(self):
        raise NotImplementedError()

    async def wait_disconnected(self):
        raise NotImplementedError()

    @property
    def disconnected(self):
        raise NotImplementedError()


class CommunicateManager(Service):
    async def warm_up(self):
        self._site = _Site()
        await self._site.run()

    @handler
    async def new_identity(self) -> Tuple[BaseCommunicatorKey, BaseCommunicator]:
        raise NotImplementedError()

