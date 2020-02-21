from asyncio import Event
from typing import Type

from ._searchable import SearchableSubclasses


class Message(SearchableSubclasses):
    def __init__(self):
        self._result = None
        self._exception = None
        self._finished = Event()
        self.to: "Service" = None

        self.args = tuple()
        self._send_kwargs = {}

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
        pass

    def _get_items(self):
        if self._result:
            yield "result", str(self._result)
        if self._exception:
            yield "_exception", str(self._exception)
        if self.args:
            yield "args", self.args
        kwargs = self.kwargs
        if kwargs:
            yield "kwargs", kwargs

        yield from self._kwargs()

    def _kwargs(self):
        for name in dir(self):
            if not name.startswith("_") and name != "kwargs" and name != "args":
                attr = getattr(self, name)
                if not callable(attr):
                    yield name, attr

    @property
    def kwargs(self):
        if self._send_kwargs:
            return self._send_kwargs

        return dict(self._kwargs())

    def __repr__(self):
        state = "✅" if self._finished.is_set() else "⏳"
        additional_repr = self._additional_repr() or dict()
        kwargs = {**dict(self._get_items()), **additional_repr}
        if kwargs:
            _s = ", ".join((f"{k}={v}" for k, v in kwargs.items()))
        else:
            _s = ""
        return f"<Message:{self.__class__.__name__}[{state}]: {_s}>"


class Shutdown(Message):
    def __init__(self, cause):
        super().__init__()
        self.cause = cause


class CreateService(Message):
    def __init__(self, service_class: Type["Service"]):
        super().__init__()
        self.service_class = service_class


class RunService(CreateService):
    pass
