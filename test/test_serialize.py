from core.serialize import serialize, deserialize
from service import Message
from test import TestedService
from test.test import will_fail


class SimpleMessage(Message):
    pass


class HardMessage(Message):
    def __init__(self, a, b, c, d):
        super().__init__()
        self.a = a
        self.b = b
        self.c = c
        self.d = d


class ArgsMessage(Message):
    def __init__(self, a, *args):
        super().__init__()
        self.a = a
        self.args = args


class TestSerialize(TestedService):
    object_collection = (
        None,
        10000000000,
        1.1,
        "test",
        [1, 2, 3, 4],
        {"lol": 2, "3": [1, 2, 3], "%": {"inside": "out"}}
    )

    async def test_objects(self):
        for item in self.object_collection:
            data = serialize(item)

            assert data

            obj = deserialize(data)

            assert obj == item, (obj, item)
            if obj is not None:
                assert not (obj is item), (obj, item)

    async def test_simple(self):
        msg = SimpleMessage()

        data = serialize(msg)

        assert "kwargs" not in data, data
        assert "args" not in data, data

        obj = deserialize(data)

        assert obj
        assert isinstance(obj, SimpleMessage)
        assert obj is not msg

    async def test_hard(self):
        msg = HardMessage(100000, "test", [1, 2, 32, 3], {"lol": 2, "3": [1, 2, 3], "%": {"inside": "out"}})

        obj = deserialize(serialize(msg))

        assert obj
        assert isinstance(obj, HardMessage)
        assert msg.a == obj.a
        assert msg.b == obj.b
        assert msg.c == obj.c
        assert msg.d == obj.d

    @will_fail
    async def test_args(self):
        raise NotImplementedError()
