import asyncio
import inspect
from time import time
from traceback import format_exc
from typing import List, Type, Iterable, Optional

from service.error import UnknownMessageType
from service.message import Message, Shutdown
from service.service import Service


class RunTests(Message):
    pass


class ListTests(Message):
    pass


class TestReport:
    def __init__(self, klass: Type[Service], method_name: str):
        self.klass = klass
        self.method_name = method_name

        self.result = None
        self.finished = False
        self.start_time = 0
        self.finish_time = 0
        self.exc: Optional[Type[Exception]] = None
        self.exc_message: Optional[str] = None

    def __repr__(self):
        return f"<TestReport: {self.klass.__name__}:{self.method_name} / {self.finished} {self.result} {self.exc}>"

    def __str__(self):
        if not self.finished:
            sign = "❓"
            info = ""
        elif self.is_good:
            sign = "✅"
            info = self.result if self.result is not None else ""
        else:
            sign = "⛔️"
            info = repr(self.exc)
            if self.exc_message:
                info += "\n"
                info += self.exc_message

        tm = self.finish_time - self.start_time

        return f"{sign} {self.klass.__name__}:{self.method_name} [{tm:.2f}s] {info}"

    @property
    def is_good(self):
        return self.finished and (self.exc is None)

    @property
    def is_bad(self):
        return self.finished and (self.exc is not None)


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

        for report in sorted(self.reports, key=lambda r: r.is_bad):
            result += f"  {report}\n"

        goods = len(tuple(filter(lambda x: x.is_good, self.reports)))

        result += f"TOTAL: {len(self.reports)} SUCCESS: {goods} BAD: {len(self.reports) - goods}\n"

        return result


class TestedService(Service):
    def __init__(self, message: Message):
        super().__init__(message)
        self._handlers[ListTests] = self._list_tests
        self._handlers[RunTests] = self._run_tests

    async def _list_tests(self, message: ListTests):
        return TestReports(*self._search_tests())

    async def _run_tests(self, message: RunTests):
        reports: TestReports = await self.get(ListTests())
        await asyncio.gather(*(
            self._run_test(report) for report in reports
        ))
        return reports

    async def _run_test(self, report: TestReport):
        try:
            method = getattr(self, report.method_name)
            report.start_time = time()
            report.result = await method()

            report.finished = True
            report.finish_time = time()
        except (Exception, AssertionError) as e:
            report.finished = True
            report.finish_time = time()

            report.exc = e
            report.exc_message = format_exc()
            self.logger.exception(report=report)

    def _search_tests(self) -> Iterable[TestReport]:
        for method_name in dir(self):
            if method_name.startswith("test_"):
                method = getattr(self, method_name)
                if inspect.iscoroutinefunction(method):
                    yield TestReport(self.__class__, method_name)
                else:
                    raise TypeError(f"Test method must be `async def`, not {type(method)}")


class TestsManager(Service):
    async def warm_up(self):
        pass

    async def process(self, message: Message):
        if isinstance(message, ListTests):
            self.logger.info("Found tested services:")

            _reports = await asyncio.gather(*(
                service_klass.get(ListTests())
                for service_klass in self.all_tested_services()
            ))

            reports = TestReports(*_reports)

            for report in reports:
                report: TestReport
                self.logger.info("🧪", report)

            return reports

        if isinstance(message, RunTests):
            _reports = await asyncio.gather(*(
                service_class.get(RunTests())
                for service_class in self.all_tested_services()
            ))

            return TestReports(*_reports)

        raise UnknownMessageType(self, message)

    def all_tested_services(self) -> List[Type[TestedService]]:
        return TestedService.all_subclasses()

    async def shutdown(self, message: Message):
        self.logger.info("Shutdown services")
        for service in self.all_tested_services():
            await service.send(Shutdown("Task finished"))


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

            return cause, exc_info

        __.__name__ = func.__name__
        return __

    return _