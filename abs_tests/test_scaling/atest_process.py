import asyncio
import os
import signal
from random import randint
from time import time, sleep

from core import Attribute
from service import Message, handler, Service
from test import TestedService, raises, xfail, skip


class DoCalc(Message):
    value: int = Attribute()
    sync_delay: int = Attribute(default=0)


class DoPing(Message):
    pass


class ServiceProcess(Service):
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

    @handler
    async def do_error(self):
        return 1 / 0


class TestServiceProcess(TestedService):
    # @skip
    async def test_pid(self):
        result, pid = await ServiceProcess.get(DoCalc(value=3))
        assert pid != os.getpid(), pid
        assert 3 ** 3 ** 2 == result

    @skip("Wait tags")
    async def test_kill(self):
        result, pid = await ServiceProcess.do_calc(0, 0)
        assert result == 1
        assert pid != os.getpid(), pid

        msg = await self.send(DoCalc(value=3, sync_delay=10))

        os.kill(pid, signal.SIGKILL)

        result, new_pid = msg.result()
        assert result == (3 ** 3) ** 2
        assert pid != new_pid

    async def _do_ping(self):
        request_start = time()
        request_accept = await ServiceProcess.get(DoPing())
        request_end = time()

        return request_accept - request_start, request_end - request_start

    @skip("Wait tags")
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

    @skip("Wait tags")
    async def test_error(self):
        with raises(ZeroDivisionError):
            await ServiceProcess.do_error()


class LocalService(Service):
    async def warm_up(self):
        self.rnd_num = randint(0, 1000000000)

    @handler
    async def get_my_pid(self):
        return os.getpid(), self.rnd_num


class ProcessSendBack(Service):
    cpu_bound = True

    @handler
    async def do_work(self):
        return os.getpid(), await LocalService.get_my_pid()

    @handler
    async def do_hark_work(self, value, epsilon):
        result, other_pid = await ServiceProcess.do_calc(value=value)
        result = result ** 0.5

        x = 0

        # Naive realization, be careful

        while abs(x ** x - result) > epsilon:
            x -= (x ** x - result) * 0.00001
            self.logger.debug(x)

        return x, other_pid, os.getpid()


class TestProcessSendBack(TestedService):
    @skip("Wait tags")
    async def test_call_local(self):
        local_pid, rnd_num = await LocalService.get_my_pid()

        sb_pid, (local_pid_returned, rnd_num_returned) = await ProcessSendBack.do_work()

        assert local_pid == os.getpid(), (local_pid, os.getpid())
        assert sb_pid != local_pid, sb_pid
        assert local_pid == local_pid_returned, (local_pid, local_pid_returned)
        assert rnd_num == rnd_num_returned, (rnd_num, rnd_num_returned)

    @skip("Wait tags")
    async def test_call_other_cpu_bound(self):
        # TODO: Parametrize
        x_orig = 0
        epsilon = 0.1

        x, other_pid, sb_pid = await ProcessSendBack.do_hark_work(x_orig, epsilon)
        assert abs(x - x_orig) < epsilon
        assert os.getpid() != other_pid
        assert os.getpid() != sb_pid
        assert sb_pid != other_pid
