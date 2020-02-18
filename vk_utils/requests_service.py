from enum import Enum

import aiohttp

from service import Service, Message
from service.error import UnknownMessageType


class _HTTPMethods(Enum):
    GET = "GET"
    POST = "POST"


class DoRequest(Message):
    def __init__(self, method: _HTTPMethods, url: str, data: dict):
        super().__init__()
        self.method = method
        self.url = url
        self.data = data


class RequestService(Service):
    def __init__(self, message: Message):
        super().__init__(message)
        self.session: aiohttp.ClientSession

    async def warm_up(self):
        self.session = aiohttp.ClientSession()

    async def process(self, message: Message):
        if isinstance(message, DoRequest):
            if message.method == _HTTPMethods.GET:
                return await self._process_get(message)

        raise UnknownMessageType(self, message)

    async def shutdown(self, message: Message):
        await self.session.close()

    @classmethod
    async def request(cls, method, url, data):
        return await cls.get(DoRequest(
            method, url, data
        ))

    @classmethod
    async def get_request(cls, url, data):
        return await cls.get(DoRequest(
            _HTTPMethods.GET, url, data
        ))

    async def _process_get(self, message: DoRequest):
        async with self.session.get(message.url, params=message.data) as resp:
            return await resp.json()
