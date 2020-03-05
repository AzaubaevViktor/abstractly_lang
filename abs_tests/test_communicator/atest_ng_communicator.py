import asyncio
from time import time
from typing import Callable, Any

from service import Message
from test import TestedService


class TestNgCommunicator(TestedService):
    async def _send_recv_step(self,
                              _from: Communicator,
                              _to: Communicator,
                              msg: Message,
                              method: Callable[[Message], Any]):
        _from.send(msg)

        _to_msg: Message = _to.recv()

        assert _to_msg.__class__ is msg.__class__
        assert _to_msg == msg

        result_ = None
        error_ = None

        try:
            result_ = method(_to_msg)
            _to_msg.set_result(result_)
        except Exception as e:
            _to_msg.set_error(e)
            error_ = e

        await msg.wait()

        assert (error_ is not None) or (result_ is not None)

        if error_:
            assert isinstance(error_, Exception)
            assert issubclass(msg.exception_nowait(), error_.__class__)
        elif result_:
            assert msg.result_nowait() == result_

    async def test_simple(self):
        key, server_comm = CommunicateManager.new_idenntity()

        client_comm = Communicator(key)

        client_comm.connect()
        assert client_comm.connected

        for simple_object in [True, False,
                              1, 0, -1,
                              "Hey", "✡️🔥♷˙∆∑ˆˆπµΩ≤µµå∆∂πæåß∂æ«åß“‘",
                              [1, 2, 3], {1: 2, '3': 4}]:
            await self._send_recv_step(
                client_comm,
                server_comm,
                Message(),
                lambda msg: simple_object
            )

            await self._send_recv_step(
                server_comm,
                client_comm,
                Message(),
                lambda msg: simple_object
            )

        tm_ = lambda msg: time()

        await asyncio.gather(*(
            self._send_recv_step(client_comm, server_comm, Message(), tm_)
            for x in range(100)
        ), *(
            self._send_recv_step(server_comm, client_comm, Message(), tm_)
            for x in range(100)
        ))

        server_comm.disconnect()
        assert server_comm.disconnnected

        await client_comm.wait_disconnected()
        assert client_comm.disconnected

    async def test_simple(self):
        key, server_comm = CommunicateManager.new_idenntity()

        client_comm = Communicator(key)

        client_comm.connect()
        assert client_comm.connected

        client_comm.disconnect()
        assert client_comm.disconnected

        await server_comm.wait_disconnected()
        assert server_comm.disconnnected
