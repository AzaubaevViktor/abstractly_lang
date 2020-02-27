import pytest

from core import AttributeStorage, Attribute


class A1(AttributeStorage):
    a = Attribute(description="a1")
    b = Attribute(description="a1")


class A2(A1):
    b = Attribute(description="a2")
    c = Attribute(description="a2")


class A3(A2):
    c = Attribute(description="a3")
    d = Attribute(description="a3")


def test_attrs_inheritance_a3():
    assert A3.__attributes__['a'].description == "a1"
    assert A3.__attributes__['b'].description == "a2"
    assert A3.__attributes__['c'].description == "a3"
    assert A3.__attributes__['d'].description == "a3"
    assert len(A3.__attributes__) == 4


def test_attr_inheritance_a2():
    assert A2.__attributes__['a'].description == "a1"
    assert A2.__attributes__['b'].description == "a2"
    assert A2.__attributes__['c'].description == "a2"
    assert len(A2.__attributes__) == 3


def test_attr_inheritance_a1():
    assert A1.__attributes__['a'].description == 'a1'
    assert A1.__attributes__['b'].description == 'a1'
    assert len(A1.__attributes__) == 2


@pytest.mark.parametrize(
    'klass', (A1, A2, A3)
)
def test_attrs(klass):
    for k, attr in klass.__attributes__.items():
        assert getattr(klass, k) is attr
        assert attr.name == k


def test_attrs_get_set():
    a1 = A1(a=1, b=2)

    assert a1.a == 1
    assert a1.b == 2

    a1.a = 3
    assert a1.a == 3


def test_attr_get_set_inh():
    a2 = A2(a=1, b=2, c=3)
    assert a2.a == 1
    assert a2.b == 2
    assert a2.c == 3

    a2.c = 4
    assert a2.c == 4


class A4(AttributeStorage):
    first_attr = Attribute()
    second_attr = Attribute()


def test_wrong_init():
    with pytest.raises(TypeError) as exc_info:
        A4(first_attr=1)

    assert "second_attr" in str(exc_info)


def test_wrong_init_extra():
    with pytest.raises(TypeError) as exc_info:
        A4(first_attr=1, second_attr=2, extra_attr=5)

    assert "extra_attr" in str(exc_info)
