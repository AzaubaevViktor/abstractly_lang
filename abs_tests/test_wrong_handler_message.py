from service import Service, handler, WrongHandlerMessageType, WrongHandlerFunc, HandlerMessageBooked
from service.message import Shutdown, Message
from test import TestedService, raises


class TestWrongHandlerMessage(TestedService):
    async def test_wrong(self):
        with raises(WrongHandlerMessageType) as exc_info:
            class S(Service):
                @handler(Shutdown)
                async def m(self):
                    pass

        assert "Shutdown" in str(exc_info)

    async def test_wrong_nont_in_start(self):
        with raises(WrongHandlerMessageType) as exc_info:
            class S(Service):
                @handler(Message, Shutdown)
                async def m(self):
                    pass

        assert "Shutdown" in str(exc_info)

    async def test_duplicate_messages(self):
        class_name = "OhMyGod"

        common_message_class = type(class_name, (Message, ), {})

        with raises(HandlerMessageBooked) as exc_info:
            class S(Service):
                @handler(common_message_class)
                async def one(self):
                    pass

                @handler(common_message_class)
                async def two(self):
                    pass

        assert class_name in str(exc_info)
        assert "one" in str(exc_info)

    async def test_not_async(self):
        with raises(WrongHandlerFunc) as exc_info:
            class S(Service):
                @handler
                def not_async(self):
                    pass

        assert "not_async" in str(exc_info)
        assert "async def" in str(exc_info)
