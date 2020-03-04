from test.test import TestedService, skip


class TestSkipped(TestedService):
    @skip("Because")
    async def test_skip(self):
        assert False, "Will not run"
