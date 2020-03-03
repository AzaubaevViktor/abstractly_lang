import inspect
from typing import Tuple, Type, Dict, Any, Sequence, List

from core import AttributeStorage, Attribute
from log import Log
from service import Service
from service._meta import MetaService


class Tag(str):
    pass


class TestInfo(AttributeStorage):
    source = Attribute(default=None)
    class_ = Attribute(default=None)
    method_name = Attribute(default=None)
    params = Attribute(default=None)
    tags = Attribute(default=None)


class MetaTestedService(MetaService):
    def __new__(mcs, name: str, bases: Tuple[Type["TestedService"]], attrs: Dict[str, Any]):
        mcs.logger = Log(mcs.__name__)
        new_attrs = MetaTestedService._garbage_tests(bases, attrs)

        class_ = super().__new__(mcs, name, bases, new_attrs)

        MetaTestedService._apply_classes(class_)

        return class_

    @classmethod
    def _garbage_tests(mcs, bases, attrs):
        __tests__ = []

        for name, method in attrs.items():
            if name.startswith("test_"):
                if inspect.iscoroutinefunction(method):
                    if hasattr(method, "__test_info__"):
                        raise NotImplementedError()
                    else:
                        method.__test_info__ = TestInfo(
                            method_name=name
                        )

                    __tests__.append(method.__test_info__)

        attrs['__tests__'] = __tests__

        return attrs

    @classmethod
    def _apply_classes(mcs, class_: Type['TestedService']):
        for info in class_.__tests__:
            info.class_ = class_


class TestedService(Service, metaclass=MetaTestedService):
    __tests__: List[TestInfo]


class TestManager(Service):
    pass
