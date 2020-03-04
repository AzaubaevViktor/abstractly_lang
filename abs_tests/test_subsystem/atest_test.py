from test.test_v1 import TestedService, xfail
from test.reports_v1 import TestReports
from test.messages_v1 import _ListTests


class TestManagerTest(TestedService):
    async def test_in_tests(self):
        reports: TestReports = await self.get(_ListTests())
        found = False
        for report in reports:
            if report.klass == self.__class__ and report.method_name == "test_in_tests":
                found = True
                break

        assert found

    @xfail("Self test")
    async def test_will_fail_assertion_error(self):
        assert False, "It's test"

    @xfail("Self test")
    async def test_will_fail_any_error(self):
        1 / 0

    @xfail("Self test")
    async def test_will_fail_exception(self):
        raise Exception("Hey")
