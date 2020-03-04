from typing import Type

from core import Attribute
from service import Service, Message, handler, BaseCommunicator, SocketIOCommunicator
from service.communicator import BaseServerInfo


class _ProxyHelloMessage(Message):
    pass


class ProxyForService(Service):
    def __init__(self, message: Message, communicator: BaseCommunicator):
        super().__init__(message)
        assert self.__class__ is ProxyForService, "You need to inherit this class first"
        self.communicator = communicator

    async def warm_up(self):
        self.logger.important(ProxyForService.mro())
        class_ = None
        raise NotImplementedError("Which class?")
        communicator = SocketIOCommunicator()
        await communicator.run()
        await ProcessSpawner.run_process(class_=class_, communicator=communicator)

        msg = await self.communicator.send_msg(_ProxyHelloMessage())

        self.logger.warning("UNAUTHORIZED CONNECTION WITH", communicator=self.communicator)

        assert await msg.result() is True

    async def _found_processor(self, msg: Message):
        return await self.communicator.send_msg(msg)


class ProcessSpawner(Service):
    @handler
    async def run_process(self, class_: Type[Service], communicator: BaseCommunicator):

        raise NotImplementedError("Start process")


class SetCommunicator(Message):
    communicator: BaseServerInfo = Attribute()


class ProxyClient(Service):
    @handler(SetCommunicator)
    async def set_communicator(self, communicator: BaseServerInfo):
        assert self.communicator is None
        self.communicator = SocketIOCommunicator(communicator)
        self.logger.important("Start connect to", communicator=communicator)
        msg = await self.communicator.receive_msg()
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


