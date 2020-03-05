import asyncio

from service import CommunicatorServer, CommunicatorClient, Message
from test import TestedService


class SimpleM(Message):
    pass


class TestCommunicator(TestedService):
    async def test_simple(self):
        MessageClass = SimpleM
        client_info = await CommunicatorServer.get_info()

        assert client_info
        assert client_info.host
        assert client_info.port
        assert client_info.client_uid

        client = CommunicatorClient(client_info)

        await client.connect()

        assert client.is_connected

        assert await CommunicatorServer.wait_for_client(info=client_info)

        server_msg = await CommunicatorServer.send_msg_to_client(info=client_info, msg=MessageClass())
        client_msg = await client.receive_msg()

        assert server_msg is not client_msg

        assert isinstance(client_msg, MessageClass)

        client_msg.set_result(123)

        assert await server_msg.result() == 123

        client_msg = await client.send_msg(SimpleM())
        server_msg = await CommunicatorServer.receive_msg_from_client(info=client_info)

        assert client_msg is not server_msg

        server_msg.set_result(321)

        assert await client_msg.result() == 321

        await CommunicatorServer.disconnect_client(info=client_info)

        assert not (await client._is_connected())
        await client.close()

    async def test_client_disconnect(self):
        client_info = await CommunicatorServer.get_info()

        client = CommunicatorClient(client_info)
        await client.connect()

        await CommunicatorServer.wait_for_client(info=client_info)

        await client.close()

        count = 0
        while await CommunicatorServer.client_connected(info=client_info):
            await asyncio.sleep(1)
            count += 1
            assert count <= 10
