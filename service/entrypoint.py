import asyncio
from typing import Dict, Union, List, Tuple, Sequence, Type, Any

from log import Log
from service import Service, Message, ServiceRunner, RunService
from service.message import Shutdown


async def entry_point():
    """ Запускает систему, передавая сообщения в сервисы """


EntryPointInfoT = Dict[
    Union[str, Type[Service]],
    Sequence[Union[Message,
                   Tuple[str, Dict]]]]

_InputDictServicesT = Dict[
    Type[Service],
    Sequence[Union[Message,
                   Tuple[str, Dict]]]]

_InputDictServicesMessagesT = Dict[
    Type[Service],
    Sequence[Message]]


class EntryPoint:
    def __init__(self, messages: EntryPointInfoT, name="__main__"):
        self.name = name
        self.logger = Log(f"EntryPoint:{self.name}")
        self.logger.important("Run", messages=messages)
        self.init_messages = messages
        self._warm_upped = False

        self.service_runner: ServiceRunner = None
        self.main_task = None

    @classmethod
    async def _main(cls, messages, name):
        await cls.cleanup()
        obj = cls(messages, name)
        await obj.warm_up()
        return await obj.run()

    @classmethod
    def main(cls, messages, name):
        result = asyncio.run(cls._main(messages, name))
        return result

    @classmethod
    def main_serializable(cls, messages, name):
        msgs = cls.main(messages, name)
        result = {}
        for msg in msgs:
            msg: Message
            result[(msg.to.__name__, msg.__class__.__name__)] = msg.result_nowait()

        return result

    def _find_services(self, messages: EntryPointInfoT) -> _InputDictServicesT:
        self.logger.info('Search services')
        new_d = {}
        for service, msgs in messages.items():
            if isinstance(service, str):
                service = Service.search(service)

            if not issubclass(service, Service):
                raise TypeError(f"{service} ({type(service)}) "
                                f"instead subclass of {Service.__class__.__name__}")

            new_d[service] = msgs

        return new_d

    def _find_messages(self, messages: _InputDictServicesT) -> _InputDictServicesMessagesT:
        self.logger.info('Search messages')
        new_d = {}
        for service, msgs in messages.items():
            processed_msgs = []
            for msg in msgs:
                if isinstance(msg, tuple):
                    msg_class_name, kwargs = msg
                    msg_class = Message.search(msg_class_name)
                    msg = msg_class(**kwargs)

                if not isinstance(msg, Message):
                    raise TypeError(f"{service} ({type(service)}) "
                                    f"instead subclass of {Message.__class__.__name__}")

                processed_msgs.append(msg)

            new_d[service] = processed_msgs

        return new_d

    async def warm_up(self):
        if self._warm_upped:
            raise RuntimeError("Already warm upped!")

        self.init_messages = self._find_messages(
            self._find_services(self.init_messages)
        )

        self._warm_upped = True

    async def _wait_for_result(self, service: Type[Service], msg: Message):
        return service, msg, await service.get(msg)

    async def run(self) -> List[Message]:
        if not self._warm_upped:
            raise RuntimeError("Call warm_up before (it's async)")

        self.init_messages: _InputDictServicesMessagesT
        self.logger.info("Create ServiceRunner")
        self.service_runner = ServiceRunner(Message())

        self.logger.info("Initilaze queue")
        Service.main_queue = asyncio.Queue()

        self.logger.info("Run ServiceRunner")

        self.main_task = asyncio.create_task(self.service_runner.run())

        self.logger.info("Send messages to run services")

        run_msgs = []
        for service_class in self.init_messages.keys():
            run_msgs.append(await ServiceRunner.send(RunService(service_class=service_class)))

        self.logger.info("Send and wait init messages")

        waited_tasks = []

        for service, msgs in self.init_messages.items():
            for msg in msgs:
                waited_tasks.append(
                    self._wait_for_result(service, msg)
                )

        results: List[Message, Any] = await asyncio.gather(*waited_tasks)

        self.logger.info("All tasks ready, Shutdown")

        await asyncio.gather(*(
            self._wait_for_result(service, Shutdown(cause="Finished from EntryPoint"))
            for service in self.init_messages.keys()
        ))

        self.logger.info("Wait while Service runner shutdowned")
        await ServiceRunner.get(Shutdown(cause="Finished main"))

        self.logger.debug("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        self.logger.important("Run results:", count=len(run_msgs))
        for msg in run_msgs:
            await msg.wait()
            self.logger.important(msg)

        self.logger.debug("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        self.logger.important("Init msgs results:", count=len(results))
        for service, msg, result in results:
            self.logger.important(service, "\n", result)

        self.logger.info("See you soon!")

        return [msg for _, msg, _ in results]

    @staticmethod
    async def cleanup():
        return await asyncio.gather(*(
            service.cleanup()
            for service in Service.all_subclasses()
        ))
