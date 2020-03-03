from asyncio import Event

from core import AttributeStorage, Attribute


class Message(AttributeStorage):
    to: "Service" = Attribute("class receiver", default=None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._result = None
        self._exception = None
        self._finished = Event()

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

    def result_nowait(self):
        return self._result

    async def exception(self):
        await self._finished.wait()
        if self._exception:
            return self._exception
        raise AttributeError("Use .result() instead")

    async def wait(self):
        await self._finished.wait()

    def _additional_repr(self) -> str:
        if self._finished.is_set():
            if self._result:
                state = f"✅ [{self._result}]"
            elif self._exception:
                state = f"⚠️ [{self._exception}]"
            else:
                state = f"❓"
        else:
            state = "⏳"

        return state


class Shutdown(Message):
    cause: str = Attribute()
