import pytest

from core import AttributeStorage, Attribute


class AS(AttributeStorage):
    a = Attribute()
    b = Attribute()


def test_serialize():
    obj = AS(a=1, b=2.1)

    data = obj.serialize()

    assert data
    assert isinstance(data, str)

    obj_r = AS.deserialize(data)

    assert obj is not obj_r

    assert obj.a == obj_r.a
    assert obj.b == obj_r.b

    assert obj == obj_r


class A2S(AS):
    a = Attribute()
    c = Attribute()


def test_serialize_inheritance():
    obj = A2S(a=1, b=2, c=3)

    data = obj.serialize()

    assert data
    assert isinstance(data, str)

    obj_r = A2S.deserialize(data)

    assert obj is not obj_r

    assert obj.a == obj_r.a
    assert obj.b == obj_r.b
    assert obj.c == obj_r.c

    assert obj == obj_r


def test_serialize_as_inside():
    obj = A2S(a=(AS(a=1, b=2), AS(a=3, b=4)),
              b=[AS(a=5, b=6), AS(a=7, b=8)],
              c={'x': AS(a=9, b=10),
                 'y': AS(a=11, b=12)})

    data = obj.serialize()

    assert data
    assert isinstance(data, str)

    obj_r = A2S.deserialize(data)

    assert obj is not obj_r

    assert obj.a == obj_r.a
    assert obj.b == obj_r.b
    assert obj.c == obj_r.c

    assert obj == obj_r


def test_serialize_wrong_class():
    obj = A2S(a=1.2, b=2.3, c=3.4)

    data = obj.serialize()

    assert data

    with pytest.raises(TypeError) as exc_info:
        AS.deserialize(data)

    assert "A2S" in exc_info
    assert "AS" in exc_info


def test_serialize_wrong_class_force():
    obj = A2S(a=1.2, b=2.3, c=3.4)

    data = obj.serialize()

    assert data

    obj_r = AS.deserialize(data, force=True)

    assert isinstance(obj_r, A2S)

    assert obj is not obj_r

    assert obj == obj_r
