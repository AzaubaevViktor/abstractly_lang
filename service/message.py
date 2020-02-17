from asyncio import Event
from typing import Type


class Message:
    def __init__(self):
        self._result = None
        self._exception = None
        self._finished = Event()
        self.to: "Service" = None

    def set_result(self, result):
        self._result = result
        self._finished.set()

    def set_error(self, exc):
        self._exception = exc
        self._finished.set()

    def ready(self) -> bool:
        return self._finished.is_set()

    def ok(self) -> bool:
        return not self._exception

    async def result(self):
        await self._finished.wait()
        if self._exception:
            raise self._exception
        return self._result

    async def exception(self):
        await self._finished.wait()
        if self._exception:
            return self._exception
        raise AttributeError("Use .result() instead")

    def _additional_repr(self) -> str:
        if self._result:
            return str(self._result)
        if self._exception:
            return str(self._exception)
        return ""

    def __repr__(self):
        state = "✅" if self._finished.is_set() else "⏳"
        return f"<Message:{self.__class__.__name__}[{state}]: {self._additional_repr()}>"


class Shutdown(Message):
    def __init__(self, cause):
        super().__init__()
        self.cause = cause


class CreateService(Message):
    def __init__(self, service_class: Type["Service"]):
        super().__init__()
        self.service_class = service_class

    def _additional_repr(self):
        return f"{self.service_class.__name__}" + super()._additional_repr()


class RunService(CreateService):
    pass
