import asyncio
import concurrent.futures
from typing import Type, Optional

from core import Attribute


from service import Service, Message, handler, EntryPoint, ServiceRunner
from service.message import Shutdown
from service.sio_comm.base import BaseCommunicator
from service.sio_comm.comm import SIOKey, ClientSioComm
from service.sio_comm.service import CommunicateManager


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

        key, self.communicator = await CommunicateManager.new_identity()
        self._run_background(
            ProcessSpawner.run_process(class_=class_, key=key)
        )

        await self.communicator.connect()

        self._run_background(
            self._run_reciever()
        )

    async def _run_reciever(self):
        while True:
            msg = await self.communicator.recv()
            self.logger.important("Recv message, put into main_queue")
            await self.main_queue.put(msg)

    async def _found_processor(self, msg: Message):
        return self.communicator.send_msg

    async def shutdown(self, message: Message):
        if self.communicator:
            await self.communicator.disconnect()


class ProcessSpawner(Service):
    async def warm_up(self):
        self.pool = concurrent.futures.ProcessPoolExecutor(max_workers=4)

    @handler
    async def run_process(self, class_: Type[Service], key: SIOKey):
        loop = asyncio.get_running_loop()
        self.logger.important("Run in executor",
                              class_=class_)
        result = await loop.run_in_executor(
            self.pool, EntryPoint.main, {
                'ServiceRunner': [("SetMainService", {'service_class_name': class_.__name__})],
                'ProxyClient': [("SetCommunicator", {'key': key})]
            }, "RunnedProcess")

        self.logger.important("Process class finished", result=result, class_=class_)

        return result

    async def shutdown(self, message: Message):
        self.pool.shutdown(wait=True)


class SetCommunicator(Message):
    key: SIOKey = Attribute()


class ProxyClient(Service):
    async def warm_up(self):
        self.communicator = None

    @handler(SetCommunicator)
    async def set_communicator(self, key: SIOKey):
        assert self.communicator is None
        self.communicator = ClientSioComm(key)

        await self.communicator.connect()

        self._run_background(self._run_waiter())

    async def _run_waiter(self):
        while True:
            msg = await self.communicator.recv()
            self.logger.important("Receive message, put into main_queue", msg=msg)

            await self.main_queue.put(msg)

    async def process(self, message: Message):
        proxy_msg = await self.communicator.send(message)
        return await proxy_msg.result()

    async def shutdown(self, message: Message):
        await ServiceRunner.send(Shutdown(cause="Remote shutdown"))
        if self.communicator:
            await self.communicator.disconnect()


