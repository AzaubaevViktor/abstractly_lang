from typing import Any

from service import Message


class BaseCommunicator:
    async def send_msg(self, msg: Message):
        raise NotImplementedError()

    async def _send_answer(self, msg: Message, answer: Any):
        raise NotImplementedError()

    async def receive_msg(self) -> Message:
        # TODO:
        #   Receive msg
        #   Return it
        #   Wait while result setted up
        #   Set answer
        raise NotImplementedError()

    async def _recv_answer(self) -> Any:
        # TODO:
        #   Found answered message
        #   Set result
        raise NotImplementedError()

    async def run(self, quiet=False):
        raise NotImplementedError()

    async def status(self):
        raise NotImplementedError()

    async def close(self):
        raise NotImplementedError()