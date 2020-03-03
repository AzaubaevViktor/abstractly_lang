from typing import List

from pytest import fixture

from test.message import RunTests
from test.test import TestManager, TestInfo
from tests.test._abs_tests.test_hello import Hello


@fixture(scope="session")
def reports_abs_tests(runner):
    msg: RunTests = runner(TestManager, RunTests(source="tests/test/_abs_tests"))

    return msg.result_nowait()


def test_run_ok(reports_abs_tests):
    assert len(reports_abs_tests) == 3

    for report in reports_abs_tests:
        assert isinstance(report, TestInfo)


def test_hello_result(reports_abs_tests, finder):
    test_hello: TestInfo = finder(reports_abs_tests, "test_hello")
    assert test_hello
    assert test_hello.class_ is Hello
    assert test_hello.method_name == "test_hello"
    assert isinstance(test_hello.result, TestResult)

