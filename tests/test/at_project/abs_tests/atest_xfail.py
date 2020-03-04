from test.test import TestedService, xfail


class TestXFail(TestedService):
    @xfail("Because")
    async def test_xfail(self):
        assert False

    @xfail("Not failed!")
    async def test_not_xfail(self):
        assert True
