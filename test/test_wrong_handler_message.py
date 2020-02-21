from service import Service, handler
from service.message import Shutdown
from test import TestedService, raises


class TestWrongHandlerMessage(TestedService):
    async def test_wrong(self):
        with raises(ValueError) as exc_info:
            class S(Service):
                @handler(Shutdown)
                def m(self):
                    pass

        assert "Shutdown" in str(exc_info.value)
