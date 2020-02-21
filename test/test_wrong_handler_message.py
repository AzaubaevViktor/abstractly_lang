from service import Service, handler
from service.message import Shutdown, Message
from test import TestedService, raises


class TestWrongHandlerMessage(TestedService):
    async def test_wrong(self):
        with raises(ValueError) as exc_info:
            class S(Service):
                @handler(Shutdown)
                def m(self):
                    pass

        assert "Shutdown" in str(exc_info.value)

    async def test_duplicate_messages(self):
        class_name = "OhMyGod"

        common_message_class = type(class_name, (Message, ), {})

        with raises(TypeError) as exc_info:
            class S(Service):
                @handler(common_message_class)
                def one(self):
                    pass

                @handler(common_message_class)
                def two(self):
                    pass

        assert class_name in exc_info
        assert "one" in exc_info
