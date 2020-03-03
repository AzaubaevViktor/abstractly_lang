from typing import Type, Iterable

from service import Service
from test.results import TestResult, TestInProgress


class TestReport:
    def __init__(self, klass: Type[Service], method_name: str):
        self.klass = klass
        self.method_name = method_name

        self.result: TestResult = TestInProgress()
        self.start_time = 0
        self.finish_time = 0

    @property
    def sort_id(self):
        return self.result.sort_id

    @property
    def full_name(self):
        return f"{self.klass.__name__}:{self.method_name}"

    def __repr__(self):
        return f"<TestReport: {self.full_name} / {self.result}>"

    def __str__(self):
        sign = self.result.sign
        info = str(self.result)

        tm = self.finish_time - self.start_time

        return f"{sign} {self.klass.__name__}:{self.method_name} [{tm:.2f}s] {info}"


class TestReports:
    def __init__(self, *reports: TestReport):
        self.reports = []
        for report in reports:
            if isinstance(report, TestReports):
                self.reports += report.reports
            else:
                self.reports.append(report)

    def append(self, report: TestReport):
        self.reports.append(report)

    def __iter__(self) -> Iterable[TestReport]:
        yield from self.reports

    def __str__(self):
        result = f"Tested services: {len(self.reports)}\n"

        for report in sorted(self.reports, key=lambda r: r.sort_id):
            result += f"  {report}\n"

        by_result_ids = {}

        for klass in sorted(TestResult.__subclasses__(), key=lambda k: k.sort_id):  # type: Type[TestResult]
            by_result_ids[klass] = 0

        for report in self.reports:
            by_result_ids[type(report.result)] += 1

        result += f"TOTAL: {len(self.reports)}\n"

        for klass, count in by_result_ids.items():
            result += f"  {klass.sign} {klass.result_id}: {count}\n"

        return result