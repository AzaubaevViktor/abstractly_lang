from core import Attribute
from service import Message
from service import BaseCommunicator, SocketIOCommunicator
from test import TestedService


class SimpleM(Message):
    pass


class HardM(Message):
    a = Attribute()
    b = Attribute()


class TestCommunicator(TestedService):
    # @skip("Not ready")
    async def test_simple(self):
        server = None
        client = None
        try:
            server: BaseCommunicator = SocketIOCommunicator()
            await server.run()

            server_info = server.server_info
            client: BaseCommunicator = SocketIOCommunicator(server_info)

            await client.run()

            msg = await server.send_msg(SimpleM())
            assert isinstance(msg, SimpleM)

            recv_msg = await client.receive_msg()
            assert isinstance(recv_msg, SimpleM)

            assert msg is not recv_msg

            recv_msg.set_result(True)

            assert True == await msg.result()
        except Exception:
            raise
        finally:
            if server:
                await server.close()
            if client:
                await client.close()

    async def test_hard(self):
        server = None
        client = None
        try:
            server: BaseCommunicator = SocketIOCommunicator()
            await server.run()

            server_info = server.server_info
            client: BaseCommunicator = SocketIOCommunicator(server_info)

            await client.run()

            msg = await server.send_msg(HardM(a=10, b=[1, 2, 3]))
            assert isinstance(msg, HardM)

            recv_msg: HardM = await client.receive_msg()
            assert isinstance(recv_msg, HardM)

            assert msg is not recv_msg

            recv_msg.set_result((recv_msg.a, recv_msg.b))

            result_ = await msg.result()
            assert [msg.a, msg.b] == result_, (msg, result_)
        except Exception:
            raise
        finally:
            if server:
                await server.close()
            if client:
                await client.close()

