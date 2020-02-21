from service import Service, Message, handler
from test import TestedService, raises


class CheckWrongHandlerUsages(TestedService):
    async def test_message_args(self):
        with raises(Exception) as exc_info:
            class M(Message):
                pass

            class S(Service):
                @handler
                def wrong(self, _ctx, additional_arg):
                    pass
