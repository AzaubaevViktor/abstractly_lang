from test import TestedService, skip


class TestTestMeta(TestedService):
    @skip
    def test_a(self):
        assert True

    @skip
    def test_b(self):
        assert True

    @skip
    def test_meta(self):
        assert self.__tests__
