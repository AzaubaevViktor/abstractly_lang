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
            attrs['__tests__'] = []
            new_attrs = attrs

        class_ = super().__new__(mcs, name, bases, new_attrs)

        MetaTestedService._apply_classes(class_)

        return class_

    @classmethod
    def _garbage_tests(mcs, bases, attrs):
        __tests__ = []

        for base in bases[::-1]:
            if base.__name__ == mcs.base_class_name:
                continue

            if not issubclass(base, TestedService):
                continue
            mcs.logger.important(current=__tests__, from_=base, what=base.__tests__)
            print(__tests__, base, base.__tests__)
            __tests__.extend(base.__tests__)

        source_path = attrs['__module__']

        for name, method in attrs.items():
            if name.startswith("test_"):
                if inspect.iscoroutinefunction(method):
                    if hasattr(method, "__test_info__"):
                        raise NotImplementedError()
                    else:
                        method.__test_info__ = TestInfo(
                            method_name=name,
                            source=source_path
                        )

                    __tests__.append(method.__test_info__)

        attrs['__tests__'] = __tests__

        return attrs

    @classmethod
    def _apply_classes(mcs, class_: Type['TestedService']):
        for info in class_.__tests__:
            if info.class_ is None:
                info.class_ = class_


class TestedService(Service, metaclass=MetaTestedService):
    __tests__: List[TestInfo]


class TestManager(Service):
    pass
