import asyncio

from core import Attribute
from service import Message
from test.test import TestedService


class X(Message):
    value = Attribute()


class Y(Message):
    max_value = Attribute()


class One(TestedService):
    async def process(self, message: Message):
        if isinstance(message, X):
            return message.value * 2

    async def test_one(self):
        results = await asyncio.gather(*(
            One.get(X(value=i)) for i in range(100)
        ))

        assert results == [x * 2 for x in range(100)]


class Two(TestedService):
    async def process(self, message: Message):
        if isinstance(message, Y):
            messages = []

            for value in range(message.max_value):
                messages.append(await One.send(X(value=value)))

            values = []

            for msg in messages:
                result_ = await msg.result()
                assert result_ == msg.value * 2
                values.append(result_)

            return sum(values)

    async def test_two(self):
        msg = await Two.send(Y(max_value=100))

        assert await msg.result() == 100 * 99
