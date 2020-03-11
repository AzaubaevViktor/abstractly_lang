import asyncio

import pytest

from service import Service, handler
from service.message import Shutdown, Message


class _DoTest(Message):
    pass


class TestS(Service):
    @handler(_DoTest)
    async def do_test(self):
        from service.sio_comm.comm import ClientSioComm
        from service.sio_comm.service import CommunicateManager

        key, server_comm = await CommunicateManager.new_identity()
        client = ClientSioComm(key)
        await client.connect()

        assert client.connected

        await server_comm.wait_connected()

        await CommunicateManager.send(Shutdown(cause="Test"))

        await asyncio.wait_for(client.wait_disconnected(), 5)

        assert client.disconnect()
        assert server_comm.disconnect()

        return True


@pytest.mark.skip
def test_comm_server(runner):
    result = runner(TestS, _DoTest())
    assert result

