import asyncio
from time import time
from typing import Callable, Any

from service import Message
from service.sio_comm.comm import ClientSioComm
from service.sio_comm.service import CommunicateManager
from service.sio_comm.base import BaseCommunicator
from test import TestedService, skip


# TODO: Переписать на фикстуры и параметризацию !!!


class TestNgCommunicator(TestedService):
    async def _send_recv_step(self,
                              _from: BaseCommunicator,
                              _to: BaseCommunicator,
                              msg: Message,
                              method: Callable[[Message], Any]):
        await _from.send(msg)

        _to_msg: Message = await _to.recv()

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

        if error_ is not None:
            assert isinstance(error_, Exception)
            assert msg.exception_nowait()
            assert isinstance(msg.exception_nowait(), error_.__class__), (msg.exception_nowait(), error_.__class__)
        elif result_ is not None:
            assert msg.result_nowait() == result_, (msg.result_nowait(), result_)

    async def test_simple(self):
        key, server_comm = await CommunicateManager.new_identity()

        client_comm = ClientSioComm(key)

        await client_comm.connect()
        assert client_comm.connected

        assert server_comm.connected

        for simple_object in [True, False,
                              1, 0, -1,
                              "Hey", "✡️🔥♷˙∆∑ˆˆπµΩ≤µµå∆∂πæåß∂æ«åß“‘",
                              [1, 2, 3], {'1': 2, '3': 4}]:
            self.logger.important("Send CLIENT => server", obj=simple_object)
            await self._send_recv_step(
                client_comm,
                server_comm,
                Message(),
                lambda msg: simple_object
            )

            self.logger.important("Send SERVER => client", obj=simple_object)
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

        await server_comm.disconnect()
        assert server_comm.disconnected

        await client_comm.wait_disconnected()
        assert client_comm.disconnected

    # @skip
    async def test_exc(self):
        key, server_comm = await CommunicateManager.new_identity()

        client_comm = ClientSioComm(key)

        await client_comm.connect()
        assert client_comm.connected

        await self._send_recv_step(
            client_comm,
            server_comm,
            Message(),
            lambda msg: 1 / 0
        )

        await self._send_recv_step(
            server_comm,
            client_comm,
            Message(),
            lambda msg: 1 / 0
        )

        await server_comm.disconnect()
        assert server_comm.disconnected

        await client_comm.wait_disconnected()
        assert client_comm.disconnected

    # @skip
    async def test_disconnect(self):
        key, server_comm = await CommunicateManager.new_identity()

        client_comm = ClientSioComm(key)

        await client_comm.connect()
        assert client_comm.connected

        await client_comm.disconnect()
        assert client_comm.disconnected

        await server_comm.wait_disconnected()
        assert server_comm.disconnected
