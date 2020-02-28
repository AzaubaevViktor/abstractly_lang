import asyncio
from asyncio import CancelledError
from random import randint
from typing import Any, Optional

import socketio
from aiohttp import web

from core import AttributeStorage, Attribute
from log import Log
from service import Message


class BaseCommunicator:
    async def send_msg(self, msg: Message):
        raise NotImplementedError()

    async def _send_answer(self, msg: Message, answer: Any):
        raise NotImplementedError()

    async def receive_msg(self) -> Message:
        # TODO:
        #   Receive msg
        #   Return it
        #   Wait while result setted up
        #   Set answer
        raise NotImplementedError()

    async def _recv_answer(self) -> Any:
        # TODO:
        #   Found answered message
        #   Set result
        raise NotImplementedError()

    async def run(self, quiet=False):
        raise NotImplementedError()

    async def status(self):
        raise NotImplementedError()

    async def close(self):
        raise NotImplementedError()


class SocketIOServerInfo(AttributeStorage):
    site: str = Attribute()
    port: int = Attribute()


class SocketIOCommunicator(BaseCommunicator):
    def __init__(self, server_info: Optional[SocketIOServerInfo] = None):
        self.logger = Log("!!Communicator")
        self.server_info = server_info
        self.task = None

        self._messages_queue = asyncio.Queue()

    async def run(self, quiet=False):
        if self.server_info is None:
            await self._start_server()
        else:
            await self._start_client()

    async def _start_server(self):
        self.logger = Log("Communicator:SERVER")
        self.logger.info("Starting server")

        self.sio = socketio.AsyncServer(async_mode="aiohttp")
        self.app = web.Application()
        self.sio.attach(self.app)

        self.sio.on("connect", self._connect)
        self.sio.on("message", self._message_server)
        self.sio.on("disconnect", self._disconnect)

        self.runner = web.AppRunner(self.app)
        await self.runner.setup()

        self.server_info = SocketIOServerInfo(
            site="localhost",
            port=randint(8081, 9999)
        )

        self.site = web.TCPSite(self.runner, self.server_info.site, self.server_info.port)
        await self.site.start()

    async def _start_client(self):
        self.logger = Log("Communicator:CLIENT")

        self.sio = socketio.AsyncClient()

        self.sio.on("connect", self._connect)
        self.sio.on("message", self._message)
        self.sio.on("disconnect", self._disconnect)

        await self.sio.connect(f"http://{self.server_info.site}:{self.server_info.port}")

        self.task = asyncio.create_task(self.sio.wait())

    async def _connect(self, *args):
        self.logger.important("Connected to", *args)

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

    async def send_msg(self, msg: Message):
        asyncio.create_task(self._send_msg(msg))
        return msg

    async def receive_msg(self) -> Message:
        self.logger.important("Wait message")

        return await self._messages_queue.get()

    async def close(self):
        self.logger.info("Stop")

        if hasattr(self, "site"):
            await self.site.stop()

        if hasattr(self, "runner"):
            await self.runner.cleanup()

        if hasattr(self, "app"):
            await self.app.cleanup()

        if self.task:
            self.task.cancel()
            try:
                await self.task
            except CancelledError:
                pass
