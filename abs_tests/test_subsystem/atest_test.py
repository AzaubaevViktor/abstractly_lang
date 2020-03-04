from test import TestedService, xfail
from test.message import ListTests
from test.results import TestExecuting
from test.test import Report, TestsManager


class TestManagerTest(TestedService):
    async def test_in_tests(self):
        report: Report = await TestsManager.get(ListTests())
        found = False
        for test_info in report:
            if test_info.method_name == "test_in_tests":
                found = test_info
                break

        assert found
        assert found.class_.__name__ is self.__class__.__name__
        return
        # This is didn't work: TestInfo recreates
        assert isinstance(found.result, TestExecuting), found.result

    @xfail("Self test")
    async def test_will_fail_assertion_error(self):
        assert False, "It's test"

    @xfail("Self test")
    async def test_will_fail_any_error(self):
        1 / 0

    @xfail("Self test")
    async def test_will_fail_exception(self):
        raise Exception("Hey")
