import asyncio

from service import Message
from test.test import TestedService


class X(Message):
    def __init__(self, value):
        super().__init__()
        self.value = value


class Y(Message):
    def __init__(self, max_value):
        super().__init__()
        self.max_value = max_value


class One(TestedService):
    async def process(self, message: Message):
        if isinstance(message, X):
            return message.value * 2

    async def test(self):
        results = await asyncio.gather(*(
            One.get(X(i)) for i in range(100)
        ))

        assert results == [x * 2 for x in range(100)]
        return True


class Two(TestedService):
    async def process(self, message: Message):
        if isinstance(message, Y):
            messages = []

            for value in range(message.max_value):
                messages.append(await One.send(X(value)))

            values = []

            for msg in messages:
                result_ = await msg.result()
                assert result_ == msg.value * 2
                values.append(result_)

            return sum(values)

    async def test(self):
        msg = await Two.send(Y(100))

        assert await msg.result() == 100 * 99

        return True
