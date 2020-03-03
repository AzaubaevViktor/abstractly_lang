from test.test import TestedService, TestInfo


class TestMetaInh(TestedService):
    async def test_a(self):
        assert True


class TestMetaInhChild(TestedService):
    async def test_b(self):
        assert True

    async def test_c(self):
        assert True


class TestMetaInhChildChild(TestedService):
    async def test_b(self):
        assert True


def test_parent():
    assert TestMetaInh.__tests__
    assert len(TestMetaInh.__tests__) == 1
    test_info = TestMetaInh.__tests__[0]
    assert test_info.class_ == TestMetaInh
    assert test_info.method_name == "test_a"


def test_child(finder):
    assert TestMetaInhChild.__tests__
    test_a: TestInfo = finder(TestMetaInhChild, "test_a")
    test_b: TestInfo = finder(TestMetaInhChild, "test_b")
    test_c: TestInfo = finder(TestMetaInhChild, "test_c")
    assert test_a.class_ is TestMetaInh
    assert test_b.class_ is TestMetaInhChild
    assert test_c.class_ is TestMetaInhChild


def test_child_child(finder):
    test_a: TestInfo = finder(TestMetaInhChildChild, "test_a")
    test_b: TestInfo = finder(TestMetaInhChildChild, "test_b")
    test_c: TestInfo = finder(TestMetaInhChildChild, "test_c")
    assert test_a.class_ is TestMetaInh
    assert test_b.class_ is TestMetaInhChildChild
    assert test_c.class_ is TestMetaInhChild
