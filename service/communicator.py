import asyncio
from asyncio import CancelledError
from random import randint
from typing import Any, Optional, TypeVar

import socketio
from aiohttp import web

from core import AttributeStorage, Attribute
from log import Log
from service import Message


class BaseServerInfo(AttributeStorage):
    def __init__(self, **kwargs):
        assert self.__class__ != BaseServerInfo
        super().__init__(**kwargs)


MsgT = TypeVar("MsgT", Message, Message)


class BaseCommunicator:
    def __init__(self,
                 server_info: Optional[BaseServerInfo] = None):
        self.server_info = server_info

    async def send_msg(self, msg: MsgT) -> MsgT:
        raise NotImplementedError()

    async def receive_msg(self) -> Message:
        raise NotImplementedError()

    async def run(self, quiet=False):
        raise NotImplementedError()

    async def status(self):
        raise NotImplementedError()

    async def close(self):
        raise NotImplementedError()


class SocketIOServerInfo(BaseServerInfo):
    site: str = Attribute()
    port: int = Attribute()


class SocketIOCommunicator(BaseCommunicator):
    def __init__(self, server_info: Optional[SocketIOServerInfo] = None):
        super().__init__(server_info)
        self.logger = Log("!!Communicator")
        self.task = None

        self._messages_queue = asyncio.Queue()

    async def run(self, quiet=False):
        if self.server_info is None:
            await self._start_server()
        else:
            await self._start_client()

    async def _start_server(self):
        self.server_info = SocketIOServerInfo(
            site="localhost",
            port=randint(8081, 9999)
        )

        self.logger = Log("Communicator:SERVER["
                          f"{self.server_info.site}:"
                          f"{self.server_info.port}"
                          "]")
        self.logger.info("Starting server")

        self.sio = socketio.AsyncServer(async_mode="aiohttp")
        self.app = web.Application()
        self.sio.attach(self.app)

        self.sio.on("connect", self._connect)
        self.sio.on("message", self._message_server)
        self.sio.on("disconnect", self._disconnect)

        self.runner = web.AppRunner(self.app)
        # web.run_app()
        await self.runner.setup()

        self.site = web.TCPSite(
            self.runner, self.server_info.site, self.server_info.port,
            shutdown_timeout=1
        )
        await self.site.start()

    async def _start_client(self):
        self.logger = Log("Communicator:CLIENT["
                          f"{self.server_info.site}:"
                          f"{self.server_info.port}"
                          "]")

        self.sio = socketio.AsyncClient()

        self.sio.on("connect", self._connect)
        self.sio.on("message", self._message)
        self.sio.on("disconnect", self._disconnect)

        await self.sio.connect(f"http://{self.server_info.site}:{self.server_info.port}")

        self.task = asyncio.create_task(self._run_client())

    async def _run_client(self):
        self.logger.info("Run client")
        await self.sio.wait()
        self.logger.info("Disconnect")
        await self.sio.disconnect()

    async def _connect(self, *args):
        what = args or self.server_info
        self.logger.important("Connected to", what)

    async def _message_server(self, sid, data):
        self.logger.important("Message from", sid=sid)
        return await self._message(data)

    async def _message(self, data):
        self.logger.important("Message:", data=data)
        msg = Message.deserialize(data, force=True)
        self.logger.important("Put into queue", msg=msg)
        await self._messages_queue.put(msg)
        self.logger.important("Wait while result", msg=msg)
        await msg.wait()

        result = {
            'result': msg._result,
            'exc': msg._exception
        }
        self.logger.important(msg=msg, result=result)
        return result

    async def _disconnect(self, *args):
        self.logger.important("Disconnect", args)

    async def _send_msg(self, msg: Message):
        data = msg.serialize()
        answer = await self.sio.call("message", data)
        self.logger.important(answer)

        if answer['result']:
            msg.set_result(answer['result'])
        elif answer['exc']:
            msg.set_error(answer['exc'])
        else:
            raise ValueError(answer)

    async def send_msg(self, msg: MsgT) -> MsgT:
        asyncio.create_task(self._send_msg(msg))
        return msg

    async def receive_msg(self) -> Message:
        self.logger.important("Wait message")

        return await self._messages_queue.get()

    async def close(self):
        self.logger.info("Stopping..")

        if hasattr(self, "site"):
            self.sio: socketio.AsyncServer
            for ns, rooms in tuple(self.sio.manager.rooms.items()):
                self.logger.info(ns=ns)
                for room, sids in tuple(rooms.items()):
                    for sid in tuple(sids.keys()):
                        self.logger.info(room=room, sid=sid)
                        await self.sio.disconnect(sid, ns)
            self.logger.info("Stopping site")
            await self.site.stop()

        if hasattr(self, "runner"):
            self.logger.info("Stopping runner")
            await self.runner.cleanup()

        if hasattr(self, "app"):
            self.logger.info("Stopping app")
            await self.app.cleanup()

        if self.task:
            self.logger.info("Stopping task")
            self.task.cancel()
            try:
                await self.task
            except CancelledError:
                pass

        self.logger.info("Finished!")
