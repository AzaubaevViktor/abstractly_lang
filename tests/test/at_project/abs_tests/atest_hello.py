import os

from service import Message
from test.test import TestedService


class HelloMsg(Message):
    pass


class Hello(TestedService):
    async def process(self, message: Message):
        if isinstance(message, HelloMsg):
            self.logger.info("Hello, world!", pid=os.getpid())
            return "Hello, world!"

    async def test_hello(self):
        msg = await Hello.send(HelloMsg())
        assert "Hello, world!" == await msg.result()

        return "Hello, test!"
