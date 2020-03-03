from test.test import TestedService, TestInfo


class TestMetaOne(TestedService):
    async def test_a(self):
        assert True


class TestMetaTwo(TestedService):
    async def test_b(self):
        assert True

    async def test_c(self):
        assert True


def test_tests_info_one_list():
    assert len(TestMetaOne.__tests__) == 1
    test_info = TestMetaOne.__tests__["test_a"]
    assert isinstance(test_info, TestInfo)
    assert test_info.class_ is TestMetaOne
    assert test_info.method_name == "test_a"
    assert test_info.source in __file__


def test_tests_info_two_list():
    assert len(TestMetaTwo.__tests__) == 2

    test_b: TestInfo = None
    test_c: TestInfo = None

    for test_info in TestMetaTwo.__tests__.values():
        if test_info.method_name == "test_b":
            test_b = test_info
        if test_info.method_name == "test_c":
            test_c = test_info

    assert test_b
    assert test_c

    assert test_b.class_ == test_c.class_ == TestMetaTwo
    assert test_b.method_name == "test_b"
    assert test_c.method_name == "test_c"
