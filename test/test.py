import asyncio
import inspect
from time import time
from traceback import format_exc
from typing import List, Type, Iterable, Optional, Union, Callable

from core import Attribute
from service import handler, BaseServiceError
from service.message import Message, Shutdown
from service.service import Service


class RunTests(Message):
    filter_by_name = Attribute(default=None)


class ListTests(Message):
    filter_by_name = Attribute(default=None)


class TestResult:
    result_id = "UNKNOWN"
    sort_id = 0
    sign = "∅"

    def __str__(self):
        raise NotImplementedError()


class TestInProgress(TestResult):
    result_id = "IN_PROGRESS"
    sort_id = 1
    sign = "❓"

    def __str__(self):
        return ""


class TestGood(TestResult):
    result_id = "GOOD"
    sort_id = 3
    sign = "✅"

    def __init__(self, result):
        self.result = result

    def __str__(self):
        return "" if self.result is None else str(self.result)


class TestFailed(TestResult):
    result_id = "FAILED"
    sort_id = 100
    sign = "⛔️"

    def __init__(self, exc, msg):
        self.exc = exc
        self.msg = msg

    def __str__(self):
        return f"{self.exc}:\n {self.msg}"


class TestSkipped(TestResult):
    result_id = "SKIPPED"
    sort_id = 2
    sign = "⏩"

    def __init__(self, cause):
        self.cause = cause

    def __str__(self):
        return str(self.cause)


class TestMustFailed(TestResult):
    result_id = "MUST FAILED"
    sort_id = 4
    sign = "⚠️"

    def __init__(self, cause, exc_info):
        self.cause = cause
        self.exc_info = exc_info

    def __str__(self):
        return f"{self.cause}: {self.exc_info}"


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


class MakeTestError(BaseServiceError):
    def __init__(self, instance, method_name, cause):
        self.instance = instance
        self.method_name = method_name
        self.cause = cause

    def __str__(self):
        return f"{self.instance.__class__.__name__}:{self.method_name} : " \
               f"{self.cause}"


class TestedService(Service):
    @handler(ListTests)
    async def list_tests(self, filter_by_name: Optional[str]):
        return TestReports(*self._search_tests(filter_by_name))

    def _search_tests(self, filter_by_name) -> Iterable[TestReport]:
        for method_name in dir(self):
            if method_name.startswith("test_"):
                method = getattr(self, method_name)
                if inspect.iscoroutinefunction(method):
                    report = TestReport(self.__class__, method_name)
                    if filter_by_name is None or (filter_by_name in report.full_name):
                        yield report
                else:
                    raise MakeTestError(
                        self, method_name,
                        f"Test is not coroutine (use `async def {method_name}(...)` instead")

    @handler(RunTests)
    async def run_tests(self, filter_by_name):
        reports: TestReports = await self.list_tests(filter_by_name)
        await asyncio.gather(*(
            self._run_single_test(report) for report in reports
        ))
        return reports

    async def _run_single_test(self, report: TestReport):
        try:
            method = getattr(self, report.method_name)
            report.start_time = time()
            result = await method()
            report.result = result if isinstance(result, TestResult) else TestGood(result)

            report.finished = True
            report.finish_time = time()
        except (Exception, AssertionError) as e:
            report.finished = True
            report.finish_time = time()

            report.result = TestFailed(e, format_exc())

            self.logger.exception(report=report)


class TestsManager(Service):
    async def warm_up(self):
        pass

    @handler(ListTests)
    async def list_tests(self, filter_by_name):
        self.logger.info("Found tested services:")

        _reports = await asyncio.gather(*(
            service_klass.get(ListTests(filter_by_name=filter_by_name))
            for service_klass in self.all_tested_services()
        ))

        reports = TestReports(*_reports)

        for report in reports:
            report: TestReport
            self.logger.info("🧪", report)

        return reports

    @handler(RunTests)
    async def run_tests(self, filter_by_name):
        _reports = await asyncio.gather(*(
            service_class.get(RunTests(filter_by_name=filter_by_name))
            for service_class in self.all_tested_services()
        ))

        return TestReports(*_reports)

    def all_tested_services(self) -> List[Type[TestedService]]:
        return TestedService.all_subclasses()

    async def shutdown(self, message: Message):
        self.logger.info("Shutdown services")
        for service in self.all_tested_services():
            await service.send(Shutdown(cause="Task finished"))


class raises:
    def __init__(self, expected_exception: Type[Exception]):
        assert isinstance(expected_exception, type), f"{expected_exception} is not class"
        assert issubclass(expected_exception, Exception), f"{expected_exception} must be subclass of Exception"
        self.expected_exception = expected_exception
        self.value = None
        self.type = None

    def __enter__(self) -> "raises":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        assert exc_type, f"Not raised {self.expected_exception}"
        assert issubclass(exc_type, self.expected_exception), f"Raised {exc_type} " \
                                                              f"instead subclass of {self.expected_exception}"

        self.type = exc_type
        self.value = exc_val
        return True

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"<raises:{self.expected_exception.__name__} " \
               f"(in fact {self.type if self.type is not None else '∅'}): " \
               f"`{self.value}` >"


def will_fail(cause: str, expected_exception: Type[Exception] = None):
    expected_exception = expected_exception or Exception

    def _(func):
        async def __(*args, **kwargs):
            with raises(expected_exception) as exc_info:
                result = await func(*args, **kwargs)

            return TestMustFailed(cause, exc_info)

        __.__name__ = func.__name__
        return __

    return _


def skip(cause: Union[Callable, str]):
    def _(func):
        async def __(*args, **kwargs):
            return TestSkipped(cause)

        __.__name__ = func.__name__
        return __

    if callable(cause):
        func = cause
        cause = "?"
        return _(func)

    return _
