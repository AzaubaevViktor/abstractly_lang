import os

from service import Message
from test.test import TestedService


class DoCalc(Message):
    def __init__(self, value: int):
        super().__init__()
        self.value = value


class TestServiceProcess(TestedService):
    cpu_bound = True

    async def process(self, message: Message):
        if isinstance(message, DoCalc):
            return message.value ** message.value ** 2, os.getpid()

    async def test(self):
        result, pid = await self.get(DoCalc(3))
        assert pid != os.getpid()
        assert 3 ** 3 ** 2 == result
