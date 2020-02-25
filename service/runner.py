import asyncio
from typing import Dict, Type

from .message import Message, CreateService, RunService
from .queue_manager import QueueManager, QueueManagerInit
from .service import Service


class ServiceRunner(Service):
    async def warm_up(self):
        self._aio_tasks.append(
            asyncio.create_task(
                QueueManager(
                    QueueManagerInit(self)
                ).run()
            )
        )

    async def process(self, message: Message):
        if isinstance(message, CreateService):
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
            elif isinstance(message, CreateService):
                self.logger.info("Starting service", instance=instance)

                self._aio_tasks.append(
                    asyncio.create_task(
                        self._just_start(instance)
                    )
                )
                return instance

    async def _just_start(self, instance):
        try:
            await instance.run()
        except Exception:
            self.logger.exception(instance=instance)
