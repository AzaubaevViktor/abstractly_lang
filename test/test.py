import asyncio
import inspect
import os
from time import time
from traceback import format_exc, format_tb, format_stack
from typing import Tuple, Type, Dict, Any, Sequence, List, Iterable, Union, Callable

from core import AttributeStorage, Attribute
from log import Log
from service import Service
from service._meta import MetaService, handler
from test.message import RunTests, ListTests
from test.results import TestNotRunning, BaseTestResult, TestSuccess, TestFailed, TestXFailed, TestSkipped


class Tag(str):
    pass


class TestInfo(AttributeStorage):
    source: str = Attribute(default=None)
    class_: Type["TestedService"] = Attribute(default=None)
    method_name: str = Attribute(default=None)
    params: Dict = Attribute(default=None)
    tags: Sequence[Tag] = Attribute(default=None)
    result: BaseTestResult = Attribute(default=None)
    start_time: float = Attribute(default=None)
    finish_time: float = Attribute(default=None)

    def __str__(self):
        if self.finish_time and self.start_time:
            tm = self.finish_time - self.start_time
            tm = f"{tm:.3f}s"
        else:
            tm = "🕰"

        return f"{self.result.SYMBOL} [{self.result.NAME:<10}] " \
               f"{self.source}::{self.class_.__name__}::{self.method_name} " \
               f"[{tm}] " \
               f"{self.result}"


class Report(AttributeStorage):
    start_time: int = Attribute()
    finish_time: int = Attribute(default=None)
    results: List[TestInfo] = Attribute(default=None)

    def __iter__(self) -> Iterable[TestInfo]:
        if self.results:
            return iter(self.results)

        return iter([])

    def __len__(self):
        if self.results:
            return len(self.results)

        return 0

    def __str__(self):
        r = "\n"
        r += "=" * 10 + " TESTS REPORT " + "=" * 10 + "\n"

        by_types = {
            result_class: 0
            for result_class
            in sorted(
                BaseTestResult.all_subclasses(),
                key=lambda rc: rc.sorted_id
            )
        }

        for test_info in sorted(
                self.results,
                key=lambda ti: (ti.result.sorted_id, ti.class_.__name__, ti.method_name)
        ):
            r += str(test_info) + "\n"

            by_types[test_info.result.__class__] += 1

        r += "\n" + "~" * 30 + "\n"

        r += f"Total execution time: {self.finish_time - self.start_time:.3f}s\n"
        r += "\n"

        total = len(self.results)
        assert total == sum(by_types.values())

        r += f"🐊 {'TOTAL':<20}: {total}\n"

        for result_class, v in by_types.items():
            r += f"{result_class.SYMBOL} {result_class.NAME:<20}: {v}\n"

        return r


class MetaTestedService(MetaService):
    base_class_name = "TestedService"
    init_name_correct: bool = None
    logger = Log(__name__)

    def __new__(mcs, name: str, bases: Tuple[Type["TestedService"]], attrs: Dict[str, Any]):
        if name == mcs.base_class_name:
            if mcs.init_name_correct is None:
                mcs.init_name_correct = True
        else:
            if mcs.init_name_correct is False:
                raise NameError(f"Base class has the different name: {name} "
                                f"instead {mcs.base_class_name}")

        if name != mcs.base_class_name:
            new_attrs = MetaTestedService._garbage_tests(bases, attrs)
        else:
            attrs['__tests__'] = {}
            new_attrs = attrs

        class_ = super().__new__(mcs, name, bases, new_attrs)

        MetaTestedService._apply_classes(class_)

        return class_

    @classmethod
    def _garbage_tests(mcs, bases, attrs):
        __tests__ = {}

        for base in bases[::-1]:
            if base.__name__ == mcs.base_class_name:
                continue

            if not issubclass(base, TestedService):
                continue
            mcs.logger.important(current=__tests__, from_=base, what=base.__tests__)
            print(__tests__, base, base.__tests__)
            __tests__.update(base.__tests__)

        source_path = attrs['__module__']

        for name, method in attrs.items():
            if name.startswith("test_"):
                if not inspect.iscoroutinefunction(method):
                    raise TypeError(f"{name} is not coroutine function, "
                                    f"but {method}")
                if hasattr(method, "__test_info__"):
                    raise NotImplementedError()
                else:
                    method.__test_info__ = TestInfo(
                        method_name=name,
                        source=source_path,
                        result=TestNotRunning()
                    )

                __tests__[name] = method.__test_info__

        attrs['__tests__'] = __tests__

        return attrs

    @classmethod
    def _apply_classes(mcs, class_: Type['TestedService']):
        for info in class_.__tests__.values():
            if info.class_ is None:
                info.class_ = class_


class TestedService(Service, metaclass=MetaTestedService):
    __tests__: Dict[str, TestInfo]

    @handler
    async def _run_test(self, test_info: TestInfo):
        assert test_info.class_ is self.__class__
        method_name = test_info.method_name
        assert hasattr(self, method_name)
        method = getattr(self, method_name)
        assert inspect.iscoroutinefunction(method)

        self.logger.info("Run test", test=test_info)
        test_info.start_time = time()
        try:
            result = await method()
            test_info.finish_time = time()
            test_info.result = result if isinstance(result, BaseTestResult) else TestSuccess(result=result)
        except (Exception, AssertionError) as e:
            test_info.finish_time = time()
            test_info.result = TestFailed(
                exc=e,
                cause=format_exc(),
                stack=format_stack()
            )

            self.logger.exception("While test")

        return test_info


class TestsManager(Service):
    PREFIX = "atest_"

    @handler(ListTests)
    async def list_tests(self, source: str):
        report = Report(start_time=time())
        classes = self._search_classes(source)
        tests = []
        for class_ in classes:
            tests.extend(class_.__tests__.values())

        report.finish_time = time()
        report.results = tests
        return report

    @handler(RunTests)
    async def run_tests(self, source: str):
        report = Report(start_time=time())

        tests = await self.list_tests(source)
        results = await asyncio.gather(*(
            test_info.class_._run_test(test_info)
            for test_info in tests
        ))

        report.finish_time = time()

        assert len(results) == len(tests)

        report.results = results

        return report

    def _search_classes(self, source: str):
        classes = set()
        self.logger.info("Search tests in folder", folder=source)

        import importlib.util

        for root, dirs, files in os.walk(source):
            for file in files:
                if file.endswith(".py") and file.startswith(self.PREFIX):
                    path = os.path.join(root, file)

                    test_hash = ".".join(path[:-len(".py")].split("/"))
                    spec = importlib.util.spec_from_file_location(
                        f"test._{test_hash}", path)
                    foo = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(foo)

                    self.logger.important(foo)
                    self.logger.important(foo.__dict__)

                    for name, attr in foo.__dict__.items():
                        if isinstance(attr, type) and \
                                issubclass(attr, TestedService) and \
                                attr is not TestedService:
                            classes.add(attr)
                            self.logger.info("Found test class", class_=attr)

        return classes


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


def xfail(cause: str, expected_exception: Type[Exception] = Exception):
    def _(func):
        async def __(*args, **kwargs):
            with raises(expected_exception) as exc_info:
                result = await func(*args, **kwargs)

            return TestXFailed(cause=cause, exc_info=exc_info)

        __.__name__ = func.__name__
        return __

    return _


def skip(cause: Union[Callable, str]):
    def _(func):
        async def __(*args, **kwargs):
            return TestSkipped(cause=cause)

        __.__name__ = func.__name__
        return __

    if callable(cause):
        func = cause
        cause = "?"
        return _(func)

    return _
