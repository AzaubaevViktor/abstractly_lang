import inspect
import os
from typing import Tuple, Type, Dict, Any, Sequence, List

from core import AttributeStorage, Attribute
from log import Log
from service import Service
from service._meta import MetaService, handler
from test.message import RunTests, ListTests
from test.results import TestNotRunning, BaseTestResult


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
    time: float = Attribute(default=None)


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


class TestManager(Service):
    PREFIX = "atest_"


    @handler(ListTests)
    async def list_tests(self, source: str):
        classes = self._search_classes(source)
        tests = []
        for class_ in classes:
            tests.extend(class_.__tests__.values())

        return tests

    @handler(RunTests)
    async def run_tests(self, source: str):
        classes = self._search_classes(source)
        pass

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
