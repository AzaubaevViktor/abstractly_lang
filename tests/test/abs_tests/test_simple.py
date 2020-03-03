from test.test import TestedService


class TestSimpleOk(TestedService):
    async def test_ok(self):
        assert True
