import asyncio
from typing import List, Type, Dict, Any

from service.message import Message
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
        good: List[Type[TestedService]] = []
        bad: Dict[Type[TestedService], Any] = {}

        for service_class in TestedService.__subclasses__():
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
                        good.append(msg.to)
                    else:
                        self.logger.warning("Test failed", service=msg.to, result=result)
                        bad[msg.to] = result
                else:
                    exc = await msg.exception()
                    self.logger.warning("Test failed", service=msg.to, exc=exc)
                    bad[msg.to] = exc

                working.remove(msg)

            await asyncio.sleep(1)

        self.logger.important("Tests finished!", good=len(good), bad=len(bad))
        self.logger.important("Good:")
        for service in good:
            self.logger.info(service)
        for service, result in bad.items():
            self.logger.warning(service, result=result)
