from asyncio import Event


class Task:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self._result = None
        self._is_complete = Event()

    async def result(self):
        await self._is_complete.wait()
        return self._result

    async def set_result(self, result):
        self._result = result
        self._is_complete.set()

    def is_complete(self) -> bool:
        return self._is_complete.is_set()


class StartTask(Task):
    pass


class ShutdownTask(Task):
    pass
