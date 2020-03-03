from core import Attribute
from service import Message


class _BaseTestMessage(Message):
    filter_by_name = Attribute(default=None)
    test_folder = Attribute(default="abs_tests")


class RunTests(_BaseTestMessage):
    pass


class ListTests(_BaseTestMessage):
    pass