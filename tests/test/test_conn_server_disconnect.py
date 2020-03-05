import asyncio

from service import Service, handler, CommunicatorServer, CommunicatorClient
from service.message import Shutdown, Message


class _DoTest(Message):
    pass


class TestS(Service):
    @handler(_DoTest)
    async def do_test(self):
        client_info = await CommunicatorServer.get_info()
        client = CommunicatorClient(client_info)
        await client.connect()

        assert client.is_connected

        await CommunicatorServer.wait_for_client(info=client_info)

        await CommunicatorServer.send(Shutdown(cause="Test"))

        count = 0
        while client.is_connected:
            await asyncio.sleep(1)
            count += 1
            assert count <= 10

        return True


def test_comm_server(runner):
    result = runner(TestS, _DoTest())
    assert result

