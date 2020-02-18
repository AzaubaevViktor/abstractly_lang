import asyncio
from typing import Dict, Type

from .message import Message, CreateService, RunService
from .service import Service


class ServiceRunner(Service):
    def __init__(self, message: Message):
        super().__init__(message)
        self.services: Dict[Type[Service], Service] = {
            ServiceRunner: self
        }

    async def process(self, message: Message):
        await self._collect_tasks()

        if isinstance(message, CreateService):
            service_class: Type[Service] = message.service_class

            if service_class._instance:
                self.logger.warning("⚠️ Instance already exist", instance=service_class._instance)
                return service_class._instance

            self.logger.debug("Create instance", klass=service_class)
            instance = service_class(message)
            self.logger.debug("Add service to services")
            self.services[service_class] = instance

            if isinstance(message, RunService):
                self.logger.info("Run service and wait while it ready", instance=instance)
                return await instance.run()
            elif isinstance(message, CreateService):
                self.logger.info("Starting service", instance=instance)

                self._aio_tasks.append(
                    asyncio.create_task(
                        self._start(instance)
                    )
                )
                return instance
            else:
                raise TypeError("Message has unknown type", type(message))

    async def _start(self, instance):
        try:
            await instance.run()
        except Exception as e:
            self.logger.exception(instance=instance)

    @classmethod
    async def get_instance(cls, service_class):
        self: ServiceRunner = cls._instance

        if service_class in self.services:
            return self.services[service_class]
        else:
            create_service_message = await ServiceRunner.send(CreateService(service_class))
            return await create_service_message.result()