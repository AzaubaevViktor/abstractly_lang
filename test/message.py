from core import Attribute
from service import Message


class RunTests(Message):
    source = Attribute(default="abs_tests")
