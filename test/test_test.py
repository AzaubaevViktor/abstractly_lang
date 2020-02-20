from test.test import TestedService, TestReports, ListTests


class TestManager(TestedService):
    async def test_in_tests(self):
        reports: TestReports = await self.get(ListTests())
        found = False
        for report in reports:
            if report.klass == self.__class__ and report.method_name == "test_in_tests":
                found = True
                break

        assert found