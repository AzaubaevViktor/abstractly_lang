from typing import Tuple, Type, Dict, Any, Sequence, List

from log import Log
from service import Service
from service._meta import MetaService


class Tag(str):
    pass


class TestInfo:
    def __init__(self,
                 source: str,
                 class_: Type[Service],
                 method_name: str,
                 params: Dict,
                 tags: Sequence[Tag]):
        self.source = source
        self.class_ = class_
        self.method_name = method_name
        self.params = params
        self.tags = tags


class MetaTestedService(MetaService):
    def __new__(mcs, name: str, bases: Tuple[Type["Service"]], attrs: Dict[str, Any]):
        mcs.logger = Log(mcs.__name__)
        new_attrs = MetaTestedService._garbage_tests(bases, attrs)

        return super().__new__(mcs, name, bases, new_attrs)

    @classmethod
    def _garbage_tests(mcs, bases, attrs):
        __tests__ = []

        return attrs


class TestedService(Service, metaclass=MetaTestedService):
    __tests__: List[TestInfo]


class TestManager(Service):
    pass
