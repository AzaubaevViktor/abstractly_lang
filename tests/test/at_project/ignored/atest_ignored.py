from test import TestedService


class IgnoredTest(TestedService):
    async def test_ignored(self):
        assert False, "This test is ignored"
