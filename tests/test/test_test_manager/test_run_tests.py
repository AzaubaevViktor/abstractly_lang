from pytest import fixture

from test.message import RunTests
from test.results import BaseTestResult, TestNotRunning, TestExecuting, TestGood, TestFailed
from test.test import TestManager, TestInfo, Report
from tests.test.at_project.abs_tests.atest_hello import Hello


@fixture(scope="session")
def reports_abs_tests(runner, project_path):
    msg: RunTests = runner(TestManager, RunTests(source=project_path))

    report = msg.result_nowait()
    assert isinstance(report, Report)
    for item in report:
        assert isinstance(item, TestInfo)
        assert isinstance(item.result, BaseTestResult)
        assert not isinstance(item.result, TestNotRunning)
        assert not isinstance(item.result, TestExecuting)

    return report


def test_run_ok(reports_abs_tests):
    assert len(reports_abs_tests) == 4

    for report in reports_abs_tests:
        assert isinstance(report, TestInfo)


def test_hello_result(reports_abs_tests, finder):
    test_hello: TestInfo = finder(reports_abs_tests, "test_hello")
    assert test_hello
    assert test_hello.class_.__name__ == "Hello"
    assert test_hello.method_name == "test_hello"
    assert isinstance(test_hello.result, BaseTestResult)

    assert isinstance(test_hello.result, TestGood)
    assert test_hello.result.result == "Hello, test!"


def test_test_wrong(reports_abs_tests, finder):
    test_wrong: TestInfo = finder(reports_abs_tests, "test_wrong")
    assert test_wrong
    assert test_wrong.class_.__name__ == "TestSimpleWrong"
    assert isinstance(test_wrong.result, TestFailed)

    assert isinstance(test_wrong.result.exc, AssertionError)
    assert test_wrong.result.cause
    assert test_wrong.result.stack
