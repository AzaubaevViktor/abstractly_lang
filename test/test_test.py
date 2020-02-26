from test.test import TestedService, TestReports, ListTests, will_fail


class TestManager(TestedService):
    async def test_in_tests(self):
        reports: TestReports = await self.get(ListTests())
        found = False
        for report in reports:
            if report.klass == self.__class__ and report.method_name == "test_in_tests":
                found = True
                break

        assert found

    @will_fail("Self test")
    async def test_will_fail_assertion_error(self):
        assert False, "It's test"

    @will_fail("Self test")
    async def test_will_fail_any_error(self):
        1 / 0

    @will_fail("Self test")
    async def test_will_fail_exception(self):
        raise Exception("Hey")
