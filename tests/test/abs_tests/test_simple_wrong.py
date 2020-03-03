from test.test import TestedService


class TestSimpleWrong(TestedService):
    async def test_wrong(self):
        assert False
