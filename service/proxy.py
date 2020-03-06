import asyncio
import concurrent.futures
from typing import Type, Optional

from core import Attribute


from service import Service, Message, handler, EntryPoint, ServiceRunner
from service.message import Shutdown


class _ProxyHelloMessage(Message):
    pass


class ProxyForService(Service):
    def __init__(self, message: Message):
        super().__init__(message)
        assert self.__class__ is not ProxyForService, "You need to inherit this class first"
        self.communicator: Optional[BaseCommunicator] = None

    async def warm_up(self):
        self.logger.important(ProxyForService.mro())
        class_ = self.__class__.mro()[1]
        self.logger.important("Start class", class_=class_)
        self.communicator = SocketIOCommunicator()
        await self.communicator.run()
        self._run_background(
            ProcessSpawner.run_process(class_=class_, communicator=self.communicator)
        )

        msg = await self.communicator.send_msg(_ProxyHelloMessage())

        self.logger.warning("UNAUTHORIZED CONNECTION WITH", communicator=self.communicator)

        assert await msg.result() is True

    async def _found_processor(self, msg: Message):
        return self.communicator.send_msg

    async def shutdown(self, message: Message):
        if self.communicator:
            msg = await self.communicator.send_msg(Shutdown(cause="Remote Shutdown"))
            self.logger.warning(await msg.result())
            await self.communicator.close()


class ProcessSpawner(Service):
    async def warm_up(self):
        self.pool = concurrent.futures.ProcessPoolExecutor(max_workers=4)

    @handler
    async def run_process(self, class_: Type[Service], communicator: "BaseCommunicator"):
        loop = asyncio.get_running_loop()
        self.logger.important("Run in executor",
                              class_=class_)
        result = await loop.run_in_executor(
            self.pool, EntryPoint.main, {
                'ServiceRunner': [("SetMainService", {'service_class_name': class_.__name__})],
                'ProxyClient': [("SetCommunicator", {'server_info': communicator.server_info})]
            }, "RunnedProcess")

        self.logger.important("Process class finished", result=result, class_=class_)

        return result

    async def shutdown(self, message: Message):
        self.pool.shutdown(wait=True)


class SetCommunicator(Message):
    server_info: "BaseServerInfo" = Attribute()


class ProxyClient(Service):
    async def warm_up(self):
        self.communicator = None

    @handler(SetCommunicator)
    async def set_communicator(self, server_info: BaseServerInfo):
        assert self.communicator is None
        self.communicator = SocketIOCommunicator(server_info)
        self.logger.important("Start connect to", communicator=server_info)
        await self.communicator.run()
        msg = await self.communicator.receive_msg()
        assert isinstance(msg, _ProxyHelloMessage), msg
        msg.set_result(True)
        self._run_background(self._run_waiter())

    async def _run_waiter(self):
        while True:
            msg = await self.communicator.receive_msg()
            self.logger.important("Message received", msg=msg)
            result = await msg.to.get(msg)
            self.logger.important("Result received")
            msg.set_result(result)

    async def process(self, message: Message):
        proxy_msg = await self.communicator.send_msg(message)
        return await proxy_msg.result()

    async def shutdown(self, message: Message):
        await ServiceRunner.send(Shutdown(cause="Remote shutdown"))
        if self.communicator:
            msg = await self.communicator.send_msg(Shutdown(cause="Remote shutdown"))
            self.logger.warning(await msg.result())
            await self.communicator.close()


