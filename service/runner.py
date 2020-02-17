import asyncio
from typing import Type

from service.base import Service
from service.error import ServiceStartError, WrongTask
from service.task import Task


class RunService(Task):
    def __init__(self, service_klass: Type[Service], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service_klass = service_klass


class ServiceRunner(Service):
    async def warm_up(self):
        assert self.services[self.__class__] is self

    @classmethod
    async def _do_run_service(cls, klass: Type['Service']):
        raise ServiceStartError(cls, "you cannot use this, start directly")

    async def process(self, task: Task):
        if isinstance(task, RunService):
            instance = task.service_klass(*task.args, **task.kwargs)
            self.logger.info("Started", instance=instance)

            return await instance.run()
        else:
            raise WrongTask(self.__class__, task)
