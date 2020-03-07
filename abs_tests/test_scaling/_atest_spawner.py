import asyncio
import os
from multiprocessing import Process

from core import Attribute
from service import EntryPoint, Service, Message, handler
from test import TestedService, skip
from tests.test.at_project.abs_tests.atest_hello import Hello

import concurrent.futures


class MS(Message):
    x = Attribute()


class S(Service):
    @handler(MS)
    async def calc(self, x):
        return x * x, os.getpid()


class TestProcessEntryPoint(TestedService):
    pool = concurrent.futures.ProcessPoolExecutor(max_workers=4)

    @skip
    async def test_simple(self):
        p = Process(target=EntryPoint.main, args=(
            {Hello.__name__: [("HelloMsg", {})]},
            "TestProcess"
        ))
        p.start()
        p.join()

    async def test_in_executor(self):
        loop = asyncio.get_running_loop()

        result = await loop.run_in_executor(
            self.pool, EntryPoint.main_serializable,
            {Hello.__name__: [("HelloMsg", {})]},
            "TestProcess")

        assert len(result) == 1

        assert list(result.values())[0] == "Hello, world!"

    async def test_in_executor_S(self):
        loop = asyncio.get_running_loop()

        result = await loop.run_in_executor(
            self.pool, EntryPoint.main_serializable,
            {S.__name__: [(MS.__name__, {'x': 3})]},
            "TestProcess")

        assert len(result) == 1

        answer = list(result.values())[0]

        assert answer[0] == 9
        assert answer[1] != os.getpid()
