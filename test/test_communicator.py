from service import Message
from service.communicator import BaseCommunicator
from test import TestedService
from test.test import will_fail


class SimpleM(Message):
    pass


class TestCommunicator(TestedService):
    @will_fail("Communicator")
    async def test_simple(self):
        server: BaseCommunicator = Communicator()
        self._run_background(server.run())

        server_info = server.info
        client: BaseCommunicator = Communicator(server_info)

        self._run_background(client.run())

        msg = await server.send_msg(SimpleM())
        assert isinstance(msg, SimpleM)

        recv_msg = await client.receive_msg()

        assert msg is not recv_msg

        recv_msg.set_result(True)

        assert True == await msg.result()
