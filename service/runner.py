import asyncio
import concurrent.futures
from typing import Dict, Type, Optional

from core import Attribute
from . import handler
from .message import Message
from .queue_manager import QueueManager, QueueManagerInit
from .service import Service


class SetMainService(Message):
    service_class_name: str = Attribute()


class ServiceRunner(Service):
    async def warm_up(self):
        self.main_service: Optional[Type[Service]] = None
        self._proxies = {}
        await self._just_start(
            QueueManager(
                QueueManagerInit(instances=(self, ))
            )
        )

    @handler(SetMainService)
    async def set_main_service(self, service_class_name):
        self.main_service = Service.search(service_class_name)
        await self.run_service(service_class=self.main_service)

    async def process(self, message: Message):
        if isinstance(message, _CreateService):
            orig_service_class: Type[Service] = message.service_class
            service_class = orig_service_class

            if orig_service_class.cpu_bound and orig_service_class != self.main_service:
                from service import ProxyForService
                if orig_service_class.__name__ not in self._proxies:
                    self._proxies[orig_service_class.__name__] = type(
                        f"Proxy{orig_service_class.__name__}",
                        (orig_service_class, ProxyForService),
                        {'__module__': "Lol in process"})

                service_class = self._proxies[orig_service_class.__name__]

            if service_class._instance:
                self.logger.warning("⚠️ Instance already exist", instance=service_class._instance)
                return service_class._instance

            self.logger.debug("Create instance", klass=service_class)
            instance = service_class(message)
            self.logger.debug("Register service", instance=instance)
            await QueueManager.register(instance=instance)

            if isinstance(message, RunService):
                self.logger.info("Run service and wait while it ready", instance=instance)
                result = await instance.run()
                return result if result is not None else True
            elif isinstance(message, _CreateService):
                self.logger.info("Starting service", instance=instance)

                await self._just_start(instance)
                return instance

    async def _just_start(self, instance):
        try:
            self._run_background(
                instance.run()
            )
        except concurrent.futures.process._RemoteTraceback:
            raise
        except Exception:
            self.logger.exception(instance=instance)

    @classmethod
    async def run_service(cls, service_class: Type[Service]):
        return await cls.get(RunService(service_class=service_class))

    @classmethod
    async def create_service(cls, service_class: Type[Service]):
        return await cls.send(_CreateService(service_class=service_class))


class _CreateService(Message):
    service_class: Type["Service"] = Attribute()


class RunService(_CreateService):
    pass
