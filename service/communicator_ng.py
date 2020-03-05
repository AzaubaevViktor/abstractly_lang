import asyncio
from asyncio import CancelledError
from random import randint
from typing import TypeVar, Dict

import socketio
from aiohttp import web

from core import AttributeStorage, Attribute
from log import Log
from service import Service, Message, handler
from concurrent.futures import TimeoutError



class ClientInfo(AttributeStorage):
    host = Attribute()
    port = Attribute()
    client_uid = Attribute()


_SendedMsgT = TypeVar("_SendedMsgT", Message, Message)


class DisconnectedError(Exception):
    def __init__(self, info):
        self.info = info


class RemoteException:
    def __init__(self, exc_class, fmt_exc, fmt_tb):
        self.exc_class = exc_class
        self.fmt_exc = fmt_exc
        self.fmt_tb = fmt_tb

    def __str__(self):
        return f"{self.exc_class} \n{self.fmt_exc}\n {self.fmt_tb}"


class _SenderReceiver:
    def __init__(self, sio):
        self.logger = Log("_SenderReceiver")
        self.sio = sio
        self._messages_queue = asyncio.Queue()

    async def new_message(self, data):
        self.logger.info("Receive msg", data)
        msg = Message.deserialize(data, force=True)

        await self._messages_queue.put(msg)

        await msg.wait()

        answer = {'result': None, 'exception': None}

        if msg.result_nowait():
            answer['result'] = msg.result_nowait()
        else:
            answer['exception'] = {
                'exc_class': msg._exception.__class__.__name__,
                'fmt_exc': str(msg._exception),
                'fmt_tb': None
            }

        return answer

    async def send_message(self, msg: Message, sid=None):
        kwargs = dict(event="message",
                      data=msg.serialize())
        if sid:
            kwargs['sid'] = sid

        result = await self.sio.call(
            **kwargs
        )

        if result['result']:
            msg.set_result(result['result'])
        elif result['exception']:
            _OrigExceptionClass = Exception.search(result['exception']['exc_class'])
            class ExceptionClass(RemoteException, _OrigExceptionClass):
                # _OrigExceptionClass for exception catching
                pass
            msg.set_error(ExceptionClass(**result['exception']))
        else:
            raise RuntimeError("Unknown result answer", result)

    async def receive_msg(self) -> Message:
        return await self._messages_queue.get()


class _Client:
    def __init__(self, sid, client_id):
        self.sid = sid
        self.client_id = client_id



class CommunicatorServer(Service):
    async def warm_up(self):
        self.clients: Dict = {}
        self.waiters: Dict[int, asyncio.Event] = {}
        self._processors: Dict[int, _SenderReceiver] = {}

        self.host = "localhost"
        self.port = randint(8100, 10000)

        self.logger.info("Starting server in",
                         host=self.host,
                         port=self.port)

        self.sio = socketio.AsyncServer(async_mode="aiohttp")
        self.app = web.Application()
        self.sio.attach(self.app)

        self.sio.on("connect", self._connect)
        self.sio.on("message", self._message)
        self.sio.on("hello", self._hello)
        self.sio.on("disconnect", self._disconnect)

        self.runner = web.AppRunner(self.app)
        # web.run_app()
        await self.runner.setup()

        self.site = web.TCPSite(
            self.runner, self.host, self.port,
            shutdown_timeout=1
        )
        await self.site.start()
        self.logger.important("Server started!")

    @handler
    async def get_info(self) -> ClientInfo:
        return ClientInfo(
            host=self.host,
            port=self.port,
            client_uid=randint(0, 100000000)
        )

    @handler
    async def wait_for_client(self, info: ClientInfo, timeout=10):
        if info.client_uid in self.clients:
            return True
        self.waiters[info.client_uid] = asyncio.Event()

        while True:
            try:
                await asyncio.wait_for(
                    self.waiters[info.client_uid].wait(),
                    timeout)
                return True
            except TimeoutError:
                return info.client_uid in self.clients

    @handler
    async def send_msg_to_client(self, info: ClientInfo, msg: _SendedMsgT) -> _SendedMsgT:
        msg: Message
        if info.client_uid not in self.clients:
            raise DisconnectedError(info)

        sid = self.clients[info.client_uid]

        self._run_background(self._send(sid, msg))
        return msg

    async def _send(self, sid, msg: Message):
        result = await self.sio.call(
            "message",
            data=msg.serialize(),
            sid=sid
        )

        if result['result']:
            msg.set_result(result['result'])
        elif result['exception']:
            msg.set_error(RemoteException(**result['exception']))
        else:
            raise RuntimeError("Unknown result answer", result)

    @handler
    async def receive_msg_from_client(self, info: ClientInfo) -> Message:
        raise NotImplementedError()

    @handler
    async def disconnect_client(self, info: ClientInfo):
        raise NotImplementedError()

    @handler
    async def client_connected(self, info: ClientInfo):
        return info.client_uid in self.clients

    async def _connect(self, sid, env):
        self.logger.info("connect client, wait for hello", sid=sid)

    async def _hello(self, sid, client_uid):
        assert client_uid not in self.clients
        assert client_uid not in self._processors

        self.clients[client_uid] = sid
        self._processors[client_uid] = _SenderReceiver(self.sio)

        if client_uid in self.waiters:
            self.waiters[client_uid].set()

        return True

    async def _message(self, sid, data):

        self._processors[]

    async def _disconnect(self, sid):
        if sid in self.clients.values():
            for k, v in list(self.clients.items()):
                if v == sid:
                    del self.clients[k]
                    break
        self.logger.info("disconnect", sid)

    async def shutdown(self, message: Message):
        await self._stop_server()

    async def _stop_server(self):
        self.sio: socketio.AsyncServer
        for ns, rooms in tuple(self.sio.manager.rooms.items()):
            self.logger.info(ns=ns)
            for room, sids in tuple(rooms.items()):
                for sid in tuple(sids.keys()):
                    self.logger.info(room=room, sid=sid)
                    await self.sio.disconnect(sid, ns)
        self.logger.debug("Stopping site")
        await self.site.stop()

        self.logger.debug("Stopping runner")
        await self.runner.cleanup()

        self.logger.debug("Stopping app")
        await self.app.cleanup()

        self.logger.info("Server stopped!")


class CommunicatorClient:
    def __init__(self, client_info: ClientInfo):
        self.client_info = client_info
        self.logger = Log(f"CommunicationClient")
        self.logger.info(client_info=client_info)
        self._is_connected = asyncio.Event()
        self._messages_queue = asyncio.Queue()

    @property
    def is_connected(self):
        return self._is_connected.is_set()

    async def _connect(self):
        self.logger.info("Connected to server")
        self.logger.info("Say hello")
        assert await self.sio.call("hello", data=self.client_info.client_uid)
        self._is_connected.set()

    async def _message(self, data):
        self.logger.info("Receive msg", data)
        msg = Message.deserialize(data, force=True)

        await self._messages_queue.put(msg)

        await msg.wait()

        answer = {'result': None, 'exception': None}

        if msg.result_nowait():
            answer['result'] = msg.result_nowait()
        else:
            answer['exception'] = {
                'exc_class': msg._exception.__class__.__name__,
                'fmt_exc': str(msg._exception),
                'fmt_tb': None
            }

        return answer

    async def _disconnect(self):
        self.logger.info("Disconnected")
        await self.sio.disconnect()
        self._is_connected.clear()

    async def connect(self):
        self.sio = socketio.AsyncClient()

        self.sio.on("connect", self._connect)
        self.sio.on("message", self._message)
        self.sio.on("disconnect", self._disconnect)

        await self.sio.connect(f"http://{self.client_info.host}:{self.client_info.port}")

        self.task = asyncio.create_task(self._run_client())

        await self._is_connected.wait()

    async def _run_client(self):
        self.logger.info("Run client")
        await self.sio.wait()
        self.logger.info("Disconnect")
        await self.sio.disconnect()

    async def send_msg(self, msg: _SendedMsgT) -> _SendedMsgT:
        raise NotImplementedError()

    async def receive_msg(self) -> Message:
        return await self._messages_queue.get()

    async def close(self):
        await self.sio.disconnect()

        self.logger.info("Stopping task")
        self.task.cancel()
        try:
            await self.task
        except CancelledError:
            pass






