import asyncio
from typing import List, Type, Dict, Any, Sequence

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


class RunTests(Service):
    async def warm_up(self):
        self.logger.info("Found tested services:")

        tests: List[DoTest] = []
        working: List[DoTest] = []
        self.good: List[Type[TestedService]] = []
        self.bad: Dict[Type[TestedService], Any] = {}

        for service_class in await self.all_services():
            service_class: TestedService
            self.logger.info("🧪", service_class)
            message = await service_class.send(DoTest())
            tests.append(message)
            working.append(message)

        while working:
            ready = tuple(msg for msg in working if msg.ready())

            for msg in ready:
                if msg.ok():
                    result = await msg.result()
                    if result is True:
                        self.logger.important("Test success", service=msg.to)
                        self.good.append(msg.to)
                    else:
                        self.logger.warning("Test failed", service=msg.to, result=result)
                        self.bad[msg.to] = result
                else:
                    exc = await msg.exception()
                    self.logger.warning("Test failed", service=msg.to, exc=exc)
                    self.bad[msg.to] = exc

                working.remove(msg)

            await asyncio.sleep(0.1)

        await self.send(Shutdown("Tasks finished"))

    async def all_services(self) -> List[Type[TestedService]]:
        return TestedService.__subclasses__()

    async def shutdown(self, message: Message):
        for service in await self.all_services():
            await service.send(Shutdown("Task finished"))

        self.logger.important("Tests finished!", good=len(self.good), bad=len(self.bad))

        self.logger.important("GOOD:")
        for service in self.good:
            self.logger.info("✅", service)

        self.logger.important("BAD:")
        for service, result in self.bad.items():
            self.logger.warning("⛔️", service, result=result)
