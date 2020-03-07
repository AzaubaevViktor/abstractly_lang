from core import Attribute
from service import Message
from test import TestedService, xfail


class SimpleMessage(Message):
    pass


class HardMessage(Message):
    a = Attribute()
    b = Attribute()
    c = Attribute()
    d = Attribute()


class TestSerialize(TestedService):
    async def test_simple(self):
        msg = SimpleMessage()

        data = msg.serialize()

        assert "kwargs" not in data, data
        assert "args" not in data, data

        obj = SimpleMessage.deserialize(data)

        assert obj
        assert isinstance(obj, SimpleMessage)
        assert obj is not msg

    async def test_hard(self):
        msg = HardMessage(a=100000,
                          b="test",
                          c=[1, 2, 32, 3],
                          d={"lol": 2, "3": [1, 2, 3], "%": {"inside": "out"}})

        obj = HardMessage.deserialize(msg.serialize())

        assert obj
        assert isinstance(obj, HardMessage)
        assert msg.a == obj.a
        assert msg.b == obj.b
        assert msg.c == obj.c
        assert msg.d == obj.d

    @xfail("Oops")
    async def test_args(self):
        raise NotImplementedError()
