from asyncio import Event

import aiofiles
from aiohttp import web
from aiohttp.abc import BaseRequest

from service import Service, Message
from service.error import UnknownMessageType
from service.message import Shutdown


class GetAddress(Message):
    pass


class GetPath(Message):
    pass


class RedirectServer(Service):
    def __init__(self, message: Message):
        super().__init__(message)
        self.app: web.Application = None
        self.runner: web.AppRunner = None
        self.site: web.TCPSite = None
        self.template: str = None

        self.path = None
        self.path_event = Event()
        self.address = "localhost"
        self.port = 8181

    async def warm_up(self):
        async with aiofiles.open("vk_utils/redirect_page.html", mode='rt') as f:
            self.template = await f.read()

        self.app = web.Application()
        self.app.add_routes([
            web.get('/redirect', self._handler_get),
            web.post('/redirect', self._handler_post)
        ])

        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.address, self.port)
        await self.site.start()

    async def _handler_get(self, request: BaseRequest):
        return web.Response(body=self.template, content_type="text/html")

    async def _handler_post(self, request: BaseRequest):
        self.path = (await request.json())['answer']
        self.path_event.set()
        return web.json_response({'status': 'ok'})

    async def process(self, message: Message):
        if isinstance(message, GetAddress):
            return f"{self.address}:{self.port}/redirect"
        if isinstance(message, GetPath):
            await self.path_event.wait()
            await self.send(Shutdown("Onetime work"))
            return self.path

        raise UnknownMessageType(self, message)

    async def shutdown(self, message: Message):
        self.logger.info("Stopping WebServer")
        await self.site.stop()
        await self.runner.cleanup()
        await self.app.cleanup()
        self.logger.info("WebServer stopped")