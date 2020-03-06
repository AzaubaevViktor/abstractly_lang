import asyncio
from asyncio import CancelledError
from random import random
from typing import Optional, Any, Dict

import socketio

from core import Attribute
from service import Message
from .base import BaseCommunicatorKey, BaseCommunicator, _MsgT
from .._background import BackgroundManager


class SIOKey(BaseCommunicatorKey):
    host = Attribute()
    port = Attribute()
    token = Attribute()


class RemoteException(Exception):
    def __init__(self, info):
        self.info = info

    def __str__(self):
        return f"<{RemoteException.__name__} of {self.__class__.mro()[1]}: {self.info}>"


class _BaseSioComm(BaseCommunicator, BackgroundManager):
    def __init__(self, key: Optional[SIOKey] = None, sio = None):
        super().__init__(key)
        self.sio = sio
        self.key = key

        self.message_queue = asyncio.Queue()

    @property
    def sid(self):
        raise NotImplementedError()

    async def send(self, msg: _MsgT) -> _MsgT:
        self._run_background(self._send(msg))
        return msg

    async def _send(self, msg: Message):
        kwargs = {
            'event': "message",
            "data": msg.serialize()
        }
        if self.sid:
            kwargs['sid'] = self.sid

        raw_data = await self.sio.call(
            **kwargs
        )

        if raw_data['raw_data']:
            msg.set_result(raw_data['raw_data'])
        elif raw_data['exception']:
            msg.set_error(await self._deserialize_exc(raw_data))
        else:
            raise RuntimeError("Unknown raw_data answer", raw_data)

    async def _deserialize_exc(self, raw_data):
        return RemoteException(**raw_data['exception'])

    async def _on_message(self, serialized_data: str):
        msg = Message.deserialize(serialized_data, force=True)

        await self.message_queue.put(msg)

        # Some hard work

        await msg.wait()

        answer = {'result': None, 'exception': None}

        if msg.result_nowait():
            answer['result'] = msg.result_nowait()
        else:
            answer['exception'] = await self._serialize_exc(msg.exception_nowait())

        return answer

    async def _serialize_exc(self, exc):
        return {
            'exc_class': exc.__class__.__name__,
            'fmt_exc': str(exc),
            'fmt_tb': None
        }

    async def recv(self) -> Message:
        return await self.message_queue.get()


class _IsConnectedStuff:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_connected = asyncio.Event()

    @property
    def connected(self):
        return self._is_connected.is_set()

    @property
    def disconnected(self):
        return not self._is_connected.is_set()

    async def wait_connected(self):
        return await self._is_connected.wait()

    async def wait_disconnected(self):
        while self._is_connected.is_set():
            await asyncio.sleep((1 + random()) / 2)

    def was_disconnected(self):
        self._is_connected.clear()

    def was_connected(self):
        self._is_connected.set()


class ServerSioComm(_IsConnectedStuff, _BaseSioComm):
    def __init__(self, **kwargs):
        self.sio: socketio.AsyncServer
        super().__init__(**kwargs)
        self.client_: "ClientInfo" = None

    @property
    def sid(self):
        return self.client_().sid

    async def connect(self):
        await self.wait_connected()


class ClientSioComm(_IsConnectedStuff, _BaseSioComm):
    def __init__(self, key: Optional[SIOKey] = None):
        self.sio: socketio.AsyncClient
        sio = socketio.AsyncClient()

        super().__init__(key=key, sio=sio)

        self.task = None

    @property
    def sid(self):
        return None

    async def connect(self):
        self.logger.info("Connect to server", host=self.key.host, port=self.key.port)

        self.sio.on("connect", self._on_connect)
        self.sio.on("message", self._on_message)
        self.sio.on("disconnect", self._on_disconnect)

        await self.sio.connect(f"http://{self.key.host}:{self.key.port}")

        self.task = asyncio.create_task(self._run_client())

        await self.wait_connected()

    async def _run_client(self):
        try:
            self.logger.info("Run client")
            await self.sio.wait()
        except CancelledError:
            pass
        finally:
            self.logger.info("Disconnect")
            await self.sio.disconnect()
            await self._on_disconnect()

    async def _on_connect(self):
        self.logger.info("Connected to server")
        self.logger.info("Say hello")
        result = await self.sio.call("hello", data=self.key.token)
        assert result, result
        self.was_connected()

    async def _on_disconnect(self):
        self.was_disconnected()

    async def disconnect(self):
        await self.sio.disconnect()

        if self.task:
            self.logger.info("Stopping task")
            self.task.cancel()
            try:
                await self.task
            except CancelledError:
                pass

        await self.wait_disconnected()


