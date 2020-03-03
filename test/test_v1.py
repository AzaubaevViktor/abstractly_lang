import asyncio
import inspect
import os
from time import time
from traceback import format_exc
from typing import Type, Iterable, Optional, Union, Callable, Set, Tuple, Dict, Any

from service import handler, BaseServiceError
from service.message import Message, Shutdown
from service.service import Service

from .messages_v1 import RunTests, ListTests
from .reports_v1 import TestReport, TestReports
from .results_v1 import TestResult, TestGood, TestFailed, TestSkipped, TestMustFailed


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
    async def list_tests(self, filter_by_name: Optional[str], **kwargs):
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
    async def run_tests(self, filter_by_name, **kwargs):
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
        self.services = set()

    @handler(ListTests)
    async def list_tests(self, filter_by_name, test_folder):
        self.logger.info("Found tested services:")

        _reports = await asyncio.gather(*(
            service_klass.get(ListTests(filter_by_name=filter_by_name))
            for service_klass in self.all_tested_services(test_folder)
        ))

        reports = TestReports(*_reports)

        for report in reports:
            report: TestReport
            self.logger.info("🧪", report)

        return reports

    @handler(RunTests)
    async def run_tests(self, filter_by_name, test_folder):
        _reports = await asyncio.gather(*(
            service_class.get(RunTests(filter_by_name=filter_by_name))
            for service_class in self.all_tested_services(test_folder)
        ))

        return TestReports(*_reports)

    def _import_files(self, test_folder: str):
        self.logger.info("Search tests from", path=test_folder)
        import importlib.util

        for root, folders, files in os.walk(test_folder):
            for file in files:
                if file.endswith(".py") and file.startswith("test_"):
                    path = os.path.join(root, file)

                    test_hash = '.'.join(path.split('/'))
                    spec = importlib.util.spec_from_file_location(
                        f"test._{test_hash}", path)
                    foo = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(foo)

                    _attrs = tuple(getattr(foo, k) for k in dir(foo))

                    classes = tuple(attr for attr in _attrs if
                                    isinstance(attr, type) and
                                    issubclass(attr, TestedService) and
                                    attr is not TestedService)
                    self.logger.info("Import test", path=path, classes=classes)

                    yield from classes

    def all_tested_services(self, folder_path: Optional[str] = None) -> Set[Type[TestedService]]:
        if folder_path is not None:
            imported = set(self._import_files(folder_path))
        else:
            imported = set()
        loaded = set(TestedService.all_subclasses())
        classes = imported | loaded
        self.services.update(classes)
        return self.services

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
