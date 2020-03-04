from core import Attribute
from service import Message


class BaseTestMessage(Message):
    source = Attribute(default="")


class RunTests(BaseTestMessage):
    pass


class ListTests(BaseTestMessage):
    pass
