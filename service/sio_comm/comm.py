import asyncio
from asyncio import CancelledError
from typing import Optional

import socketio

from core import Attribute
from service.sio_comm.base import BaseCommunicatorKey, BaseCommunicator


class SIOKey(BaseCommunicatorKey):
    host = Attribute()
    port = Attribute()
    token = Attribute()


class _BaseSioComm(BaseCommunicator):
    def __init__(self, key: Optional[SIOKey] = None, sio = None):
        super().__init__(key)
        self.sio = sio
        self.key = key

        self.message_queue = asyncio.Queue()


class ServerSioComm(_BaseSioComm):
    async def connect(self):
        self.sio: socketio.AsyncServer
        # Server already run
        pass


class ClientSioComm(_BaseSioComm):
    def __init__(self, key: Optional[SIOKey] = None):
        sio = socketio.AsyncClient()

        super().__init__(key=key, sio=sio)

        self._is_connected = asyncio.Event()

        self.task = None

    @property
    async def connected(self):
        return self._is_connected.is_set()

    @property
    async def disconnected(self):
        return not self._is_connected.is_set()

    async def connect(self):
        self.logger.info("Connect to server", host=self.key.host, port=self.key.port)

        self.sio.on("connect", self._on_connect)

        await self.sio.connect(f"http://{self.key.host}:{self.key.port}")

        self.task = asyncio.create_task(self._run_client())

        await self._is_connected.wait()

    async def _run_client(self):
        self.logger.info("Run client")
        await self.sio.wait()
        self.logger.info("Disconnect")
        await self.sio.disconnect()

    async def _on_connect(self):
        self.logger.info("Connected to server")
        self.logger.info("Say hello")
        result = await self.sio.call("hello", data=self.key.token)
        assert result, result
        self._is_connected.set()

    async def disconnect(self):
        await self.sio.disconnect()

        if self.task:
            self.logger.info("Stopping task")
            self.task.cancel()
            try:
                await self.task
            except CancelledError:
                pass

