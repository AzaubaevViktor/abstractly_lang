from parser import CharParser, AndParser, OrParser, KeyArgument, FuncParser, RepeatParser


def test_char_eq():
    assert CharParser("x") == CharParser("x")


def binary_parser_assert(parser):
    x = CharParser("x")
    y = CharParser("y")

    p1 = parser(x, y)
    p2 = parser(x, y)

    assert p1 == p2


def test_and_eq():
    binary_parser_assert(AndParser)


def test_or_eq():
    binary_parser_assert(OrParser)


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
