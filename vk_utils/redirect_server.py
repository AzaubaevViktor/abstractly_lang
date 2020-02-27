from asyncio import Event

import aiofiles
from aiohttp import web
from aiohttp.abc import BaseRequest

from service import Message, handler
from service.message import Shutdown
from test import TestedService


class RedirectServer(TestedService):
    def __init__(self, message: Message):
        super().__init__(message)
        self.app: web.Application = None
        self.runner: web.AppRunner = None
        self.site: web.TCPSite = None
        self.template: str = None

        self.data = None
        self.data_received = Event()

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
        path = (await request.json())['answer']
        self.data = dict(item.split('=') for item in path.split("&"))
        self.data_received.set()
        return web.json_response({'status': 'ok'})

    @handler
    async def get_address(self):
        return f"{self.address}:{self.port}/redirect"

    @handler
    async def get_data(self):
        await self.data_received.wait()
        await self.send(Shutdown(casue="Onetime work"))
        return self.data

    async def shutdown(self, message: Message):
        self.logger.info("Stopping WebServer")
        await self.site.stop()
        await self.runner.cleanup()
        await self.app.cleanup()
        self.logger.info("WebServer stopped")

    # TODO: Add test
