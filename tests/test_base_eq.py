import pytest
from parser import CharParser, AndParser, OrParser, KeyArgument, FuncParser, RepeatParser


def test_char_eq():
    assert CharParser("x") == CharParser("x")


@pytest.mark.parametrize("parser", [AndParser, OrParser])
def test_binary_parser_assert(parser):
    x = CharParser("x")
    y = CharParser("y")

    p1 = parser(x, y)
    p2 = parser(x, y)

    assert p1 == p2


def test_key_argument_eq():
    x = CharParser("x")

    assert KeyArgument("y", x) == KeyArgument("y", x)


def test_func_eq():
    def f(): pass
    x = CharParser("x")

    assert FuncParser(x, f) == FuncParser(x, f)


def test_repeat_eq():
    x = CharParser("x")

    assert RepeatParser(x) == RepeatParser(x)
    assert RepeatParser(x, _from=10, _to=100) == RepeatParser(x, _from=10, _to=100)


def test_char_not_eq():
    assert CharParser("y") != CharParser("x")


@pytest.mark.parametrize("parser", [AndParser, OrParser])
def test_binary_parser_not_assert(parser):
    x = CharParser("x")
    y = CharParser("y")

    p1 = parser(x, x)
    p2 = parser(y, y)

    assert p1 != p2


def test_key_argument_not_eq():
    x = CharParser("x")
    y = CharParser("y")

    assert KeyArgument("b", x) != KeyArgument("a", x)
    assert KeyArgument("y", x) != KeyArgument("y", y)


def test_func_not_eq():
    def f(): pass
    def g(): pass
    x = CharParser("x")
    y = CharParser("y")

    assert FuncParser(x, f) != FuncParser(y, f)
    assert FuncParser(x, f) != FuncParser(x, g)


def test_repeat_not_eq():
    x = CharParser("x")
    y = CharParser("y")

    assert RepeatParser(x) != RepeatParser(y)
    assert RepeatParser(x, _from=1, _to=100) != RepeatParser(x, _from=10, _to=100)
    assert RepeatParser(x, _from=10, _to=10) != RepeatParser(x, _from=10, _to=100)
