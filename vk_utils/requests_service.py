from enum import Enum
from typing import Any

import aiohttp

from service import Message, handler, Service


class _HTTPMethods(Enum):
    GET = "GET"
    POST = "POST"


class RequestService(Service):
    def __init__(self, message: Message):
        super().__init__(message)
        self.session: aiohttp.ClientSession

    async def warm_up(self):
        self.session = aiohttp.ClientSession()

    async def shutdown(self, message: Message):
        await self.session.close()

    @handler
    async def _request(self, method: _HTTPMethods, url: str, data: Any = None):
        if method is _HTTPMethods.GET:
            return await self.get_request(url, data)
        else:
            raise NotImplementedError(f"Request for {method.name} not implemented yet")

    @handler
    async def get_request(self, url: str, data=None):
        async with self.session.get(url, params=data, timeout=10) as resp:
            return await resp.json()

