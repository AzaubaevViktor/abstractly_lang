from typing import List

from pytest import fixture

from test.message import ListTests
from test.results import BaseTestResult, TestNotRunning
from test.test import TestManager, TestInfo


@fixture(scope='session')
def tests_list(runner, project_path):
    msg: ListTests = runner(TestManager, ListTests(source=project_path))
    result: List[TestInfo] = msg.result_nowait()
    assert isinstance(result, list)
    for item in result:
        assert isinstance(item, TestInfo)
        assert isinstance(item.result, BaseTestResult)
        assert isinstance(item.result, TestNotRunning)

    return result


def test_list_count(tests_list):
    assert len(tests_list) == 7


def test_list_tests(tests_list, finder):
    test_hello = finder(tests_list, "test_hello")
    assert isinstance(test_hello, TestInfo)
    assert test_hello.class_.__name__ == "Hello"
    assert test_hello.method_name == "test_hello"


def test_tests_from_service(finder, tests_list):
    test_calc = finder(tests_list, "test_calc")
    assert test_calc.class_.__name__ == "TestCalculator"
