import asyncio
import os
import signal
from time import time, sleep

from service import Message, handler
from test.test import TestedService


class DoCalc(Message):
    def __init__(self, value: int, sync_delay = 0):
        super().__init__()
        self.value = value
        self.sync_delay = sync_delay


class DoPing(Message):
    pass


class TestServiceProcess(TestedService):
    cpu_bound = True

    @handler(DoCalc)
    async def do_calc(self, value, sync_delay=0):
        if sync_delay:
            self.logger.info("Do sync delay...")
            sleep(sync_delay)
        return value ** value ** 2, os.getpid()

    @handler(DoPing)
    async def do_ping(self):
        return time()

    async def test_pid(self):
        result, pid = await self.get(DoCalc(3))
        assert pid != os.getpid(), pid
        assert 3 ** 3 ** 2 == result

    async def test_kill(self):
        result, pid = await self.do_calc(0, 0)
        assert result == 1
        assert pid != os.getpid()

        msg = await self.send(DoCalc(3, 10))

        os.kill(pid, signal.SIGKILL)

        result, new_pid = msg.result()
        assert result == 3 ** 3 ** 2
        assert pid != new_pid

    async def _do_ping(self):
        request_start = time()
        request_accept = await self.get(DoPing())
        request_end = time()

        return request_accept - request_start, request_end - request_start

    async def test_ping(self):
        self.logger.info("Linear ping")

        linear = []

        for i in range(100):
            linear.append(await self._do_ping())

        parallel = await asyncio.gather(*(self._do_ping() for _ in range(100)))

        self._log_stats("Linear  ", linear)
        self._log_stats("Parallel", parallel)

    def _log_stats(self, name, pairs):
        self.logger.important(f"{name} ping result:")
        self.logger.info("  Accept:", **self._log_stats_one(
            [x[0] for x in pairs]
        ))
        self.logger.info("  End   :", **self._log_stats_one(
            [x[1] for x in pairs]
        ))

    def _log_stats_one(self, times):
        return {
            'min': f"{min(times) * 1000:.3f}ms",
            'avg': f"{sum(times) / len(times) * 1000:.3f}ms",
            'mid': f"{sorted(times)[len(times) // 2] * 1000:.3f}ms",
            'max': f"{max(times) * 1000:.3f}ms",
        }



