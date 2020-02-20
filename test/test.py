import asyncio
from time import time
from typing import List, Type, Dict, Any

from log import Log
from service.error import UnknownMessageType
from service.message import Message, Shutdown
from service.service import Service
from test.messages import DoTest


class TestedService(Service):
    async def _apply_task(self, message: Message):
        if isinstance(message, DoTest):
            try:
                message.set_result(await self.test())
            except Exception as e:
                self.logger.exception(message=message)
                message.set_error(e)
        else:
            await super(TestedService, self)._apply_task(message)

    async def test(self):
        return True


class RunTests(Message):
    pass


class ListTests(Message):
    pass


class TestReport:
    def __init__(self, services):
        self.logger = Log("Test:report")
        self.services: List[Type[TestedService]] = services
        self._goods: List[Type[TestedService]] = []
        self._bads: Dict[Type[TestedService], Any] = {}
        self._times: Dict[Type[TestedService], float] = {}
        self.start_time: float = None

    def good(self, msg: Message):
        self._times[msg.to] = time() - self.start_time
        self.logger.important("Test success", service=msg.to)
        self._goods.append(msg.to)

    def bad(self, msg: Message, result):
        self._times[msg.to] = time() - self.start_time
        self.logger.warning("Test failed", service=msg.to, result=result)
        self._bads[msg.to] = result

    def __str__(self):
        result = f"Tested services: {len(self.services)}\n"

        result += "GOOD:\n"
        for service in self._goods:
            result += f"  ✅ {service} [{self._times[service]:.2f}s]\n"

        result += "BAD:\n"
        for service, test_result in self._bads.items():
            result += f"  ⛔️ {service}:[{self._times[service]:.2f}s]\n" \
                      f"     {test_result}\n"

        result += f"\nSUCCESS: {len(self._goods)}"

        result += f" BAD: {len(self._bads)}\n"

        return result


class TestsManager(Service):
    async def warm_up(self):
        pass

    async def process(self, message: Message):
        if isinstance(message, ListTests):
            self.logger.info("Found tested services:")

            report = TestReport(self.all_services())

            for service_class in report.services:
                service_class: TestedService
                self.logger.info("🧪", service_class)

            return report

        if isinstance(message, RunTests):
            report: TestReport = await self.get(ListTests())

            report.start_time = time()

            tests = await asyncio.gather(*(
                service_class.send(DoTest())
                for service_class in self.all_services()
            ))

            working = tests[:]

            while working:
                ready = tuple(msg for msg in working if msg.ready())

                for msg in ready:
                    if msg.ok():
                        result = await msg.result()
                        if result is True:
                            report.good(msg)
                        else:
                            report.bad(msg, result)
                    else:
                        exc = await msg.exception()
                        report.bad(msg, exc)

                    working.remove(msg)

                await asyncio.sleep(0.1)

            self.logger.important("Good tests:", good=len(report._goods))
            if report._bads:
                self.logger.warning("Bad tests:", good=len(report._bads))


            return report

        raise UnknownMessageType(self, message)

    def all_services(self) -> List[Type[TestedService]]:
        return TestedService.__subclasses__()

    async def shutdown(self, message: Message):
        self.logger.info("Shutdown services")
        for service in self.all_services():
            await service.send(Shutdown("Task finished"))
