from core import Attribute
from service import Message


class _BaseTestMessage(Message):
    filter_by_name = Attribute(default=None)
    test_folder = Attribute(default="abs_tests")


class _RunTests(_BaseTestMessage):
    pass


class _ListTests(_BaseTestMessage):
    pass
