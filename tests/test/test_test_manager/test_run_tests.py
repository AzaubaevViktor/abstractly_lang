from pytest import fixture

from test.message import RunTests
from test.results import BaseTestResult, TestNotRunning, TestExecuting
from test.test import TestManager, TestInfo
from tests.test.at_project.abs_tests.atest_hello import Hello


@fixture(scope="session")
def reports_abs_tests(runner, project_path):
    msg: RunTests = runner(TestManager, RunTests(source=project_path))

    result = msg.result_nowait()
    assert isinstance(result, list)
    for item in result:
        assert isinstance(item, TestInfo)
        assert isinstance(item.result, BaseTestResult)
        assert not isinstance(item.result, TestNotRunning)
        assert not isinstance(item.result, TestExecuting)

    return result


def test_run_ok(reports_abs_tests):
    assert len(reports_abs_tests) == 3

    for report in reports_abs_tests:
        assert isinstance(report, TestInfo)


def test_hello_result(reports_abs_tests, finder):
    test_hello: TestInfo = finder(reports_abs_tests, "test_hello")
    assert test_hello
    assert test_hello.class_ is Hello
    assert test_hello.method_name == "test_hello"
    assert isinstance(test_hello.result, BaseTestResult)

