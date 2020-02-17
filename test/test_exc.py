from service import Message
from test.test import TestedService


class Z(Message):
    def __init__(self, value):
        super().__init__()
        self.value = value


class TestException(TestedService):
    async def process(self, message: Message):
        if isinstance(message, Z):
            return 1 / message.value

    async def test(self):
        assert await TestException.get(Z(2)) == 1 / 2

        try:
            await TestException.get(Z(0))
        except ZeroDivisionError:
            self.logger.info("Nice")

        msg = await TestException.send(Z(0))

        e = await msg.exception()
        assert isinstance(e, ZeroDivisionError)

        return True
