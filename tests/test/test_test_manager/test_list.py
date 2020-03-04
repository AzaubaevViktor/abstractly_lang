from typing import List

from pytest import fixture

from test.message import ListTests
from test.test import TestManager, TestInfo
from tests.test._abs_tests.test_hello import Hello


@fixture(scope='session')
def tests_list(runner):
    msg: ListTests = runner(TestManager, ListTests(source="tests/test/_abs_tests"))
    result: List[TestInfo] = msg.result_nowait()
    assert isinstance(result, list)
    for item in result:
        assert isinstance(item, TestInfo)

    return result


def test_list_tests(tests_list, finder):
    test_hello = finder(tests_list, "test_hello")
    assert isinstance(test_hello, TestInfo)
    assert test_hello.class_.__name__ == "Hello"
    assert test_hello.method_name == "test_hello"
    assert test_hello.result is None
