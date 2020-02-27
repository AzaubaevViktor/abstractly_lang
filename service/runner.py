import asyncio
from typing import Dict, Type

from core import Attribute
from .message import Message
from .queue_manager import QueueManager, QueueManagerInit
from .service import Service


class ServiceRunner(Service):
    async def warm_up(self):
        await self._just_start(
            QueueManager(
                QueueManagerInit(instances=(self, ))
            )
        )

    async def process(self, message: Message):
        if isinstance(message, _CreateService):
            service_class: Type[Service] = message.service_class

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
