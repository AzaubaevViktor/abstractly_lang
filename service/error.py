from typing import Type


class BaseServiceError(Exception):
    pass


class ServiceStartError(BaseServiceError):
    def __init__(self, klass: Type['Service'], msg: str):
        self.klass = klass
        self.msg = msg

    def __str__(self):
        return f"Service {self.klass}: {self.msg}"


class WrongTask(BaseServiceError):
    def __init__(self, klass: Type['Service'], task: 'Task', msg: str = ""):
        self.klass = klass
        self.task = task
        self.msg = msg

    def __str__(self):
        return f"Service {self.klass} cannot process {self.task}: {self.msg}"


class ServiceSearchError(BaseServiceError):
    def __init__(self, name, services=None):
        self.services = services
        self.name = name

    def __str__(self):
        return f"Service `{self.name}` not found. Use one of them: {self.services}\n" \
               f"  OR import file with this service\n" \
               f"  OR check desired class is subclass of `Service`"
