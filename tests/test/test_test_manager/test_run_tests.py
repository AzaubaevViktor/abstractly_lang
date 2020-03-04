from pytest import fixture

from test.message import RunTests
from test.results import BaseTestResult, TestNotRunning, TestExecuting, TestSuccess, TestFailed, TestXFailed
from test.test import TestsManager, TestInfo, Report, raises


@fixture(scope="session")
def reports_abs_tests(runner, project_path) -> Report:
    msg: RunTests = runner(TestsManager, RunTests(source=project_path))

    report = msg.result_nowait()
    assert isinstance(report, Report)
    for item in report:
        assert isinstance(item, TestInfo)
        assert isinstance(item.result, BaseTestResult)
        assert not isinstance(item.result, TestNotRunning)
        assert not isinstance(item.result, TestExecuting)

    return report


def test_run_ok(reports_abs_tests):
    assert len(reports_abs_tests) == 7

    for report in reports_abs_tests:
        assert isinstance(report, TestInfo)


def test_hello_result(reports_abs_tests, finder):
    test_hello: TestInfo = finder(reports_abs_tests, "test_hello")
    assert test_hello
    assert test_hello.class_.__name__ == "Hello"
    assert test_hello.method_name == "test_hello"
    assert isinstance(test_hello.result, BaseTestResult)

    assert isinstance(test_hello.result, TestSuccess)
    assert test_hello.result.result == "Hello, test!"


def test_test_wrong(reports_abs_tests, finder):
    test_wrong: TestInfo = finder(reports_abs_tests, "test_wrong")
    assert test_wrong
    assert test_wrong.class_.__name__ == "TestSimpleWrong"
    assert isinstance(test_wrong.result, TestFailed)

    assert isinstance(test_wrong.result.exc, AssertionError)
    assert test_wrong.result.cause
    assert test_wrong.result.stack


def test_test_xfail_true(reports_abs_tests, finder):
    test_xfail: TestInfo = finder(reports_abs_tests, "test_xfail")
    assert isinstance(test_xfail.result, TestXFailed)
    assert isinstance(test_xfail.result.exc_info, raises)
    assert test_xfail.result.cause


def test_test_xfail_false(reports_abs_tests, finder):
    test_not_xfail: TestInfo = finder(reports_abs_tests, "test_not_xfail")
    assert isinstance(test_not_xfail.result, TestFailed)
    assert isinstance(test_not_xfail.result.exc, AssertionError)


def test_report(reports_abs_tests):
    s = str(reports_abs_tests)
    assert s
    print(s)

    assert str(len(reports_abs_tests)) in s

    for item in reports_abs_tests:
        item: TestInfo
        assert item.method_name in s
        assert item.class_.__name__ in s


def test_test_ignored(reports_abs_tests, finder):
    with raises(AssertionError):
        finder(reports_abs_tests, "test_ignored")
