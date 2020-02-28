from service import Message
from service import BaseCommunicator, SocketIOCommunicator
from test import TestedService
from test.test import will_fail, skip


class SimpleM(Message):
    pass


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

            assert msg is not recv_msg

            recv_msg.set_result(True)

            assert True == await msg.result()
        except Exception:
            pass
        finally:
            if server:
                await server.close()
            if client:
                await client.close()
            raise
