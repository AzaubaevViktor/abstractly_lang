from typing import List

from pytest import fixture

from test.message import RunTests
from test.test import TestManager, TestInfo


@fixture(scope="session")
def reports_abs_tests(runner):
    msg: RunTests = runner(TestManager, RunTests(source="tests/test/_abs_tests"))

    return msg.result_nowait()


def test_run_ok(reports_abs_tests):
    assert len(reports_abs_tests) == 3

    for report in reports_abs_tests:
        assert isinstance(report, TestInfo)



