from core import Attribute
from service import Message
from test.test import TestedService


class Z(Message):
    value = Attribute()


class TestException(TestedService):
    async def process(self, message: Message):
        if isinstance(message, Z):
            return 1 / message.value

    async def test_get_exc(self):
        assert await TestException.get(Z(value=2)) == 1 / 2

        try:
            await TestException.get(Z(value=0))
        except ZeroDivisionError:
            self.logger.info("Nice")

    async def test_send_exc(self):

        msg = await TestException.send(Z(value=0))

        e = await msg.exception()
        assert isinstance(e, ZeroDivisionError)
