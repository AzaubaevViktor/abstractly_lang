from parser import CharParser, AndParser, OrParser, KeyArgument, FuncParser, RepeatParser


def test_char_hash():
    assert hash(CharParser("x")) == hash(CharParser("x"))


def binary_parser_assert(parser):
    x = CharParser("x")
    y = CharParser("y")

    p1 = parser(x, y)
    p2 = parser(x, y)

    assert hash(p1) == hash(p2)


def test_and_hash():
    binary_parser_assert(AndParser)


def test_or_hash():
    binary_parser_assert(OrParser)


def test_key_argument_hash():
    x = CharParser("x")

    assert hash(KeyArgument("y", x)) == hash(KeyArgument("y", x))


def test_func_hash():
    def f(): pass
    x = CharParser("x")

    assert hash(FuncParser(x, f)) == hash(FuncParser(x, f))


def test_repeat_hash():
    x = CharParser("x")

    assert hash(RepeatParser(x)) == hash(RepeatParser(x))
    assert hash(RepeatParser(x, _from=10, _to=100)) == hash(RepeatParser(x, _from=10, _to=100))


def test_char_not_hash():
    assert hash(CharParser("x")) != hash(CharParser("y"))


def binary_parser_not_assert(parser):
    x = CharParser("x")
    y = CharParser("y")

    p1 = parser(x, x)
    p2 = parser(y, y)

    assert hash(p1) != hash(p2)


def test_and_not_hash():
    binary_parser_not_assert(AndParser)


def test_or_not_hash():
    binary_parser_not_assert(OrParser)


def test_key_argument_not_hash():
    x = CharParser("x")
    y = CharParser("y")

    assert hash(KeyArgument("y", x)) != hash(KeyArgument("y", y))
    assert hash(KeyArgument("x", x)) != hash(KeyArgument("y", x))


def test_func_not_hash():
    def f(): pass
    def g(): pass
    x = CharParser("x")
    y = CharParser("y")

    assert hash(FuncParser(x, f)) != hash(FuncParser(y, f))
    assert hash(FuncParser(x, f)) != hash(FuncParser(x, g))


def test_repeat_not_hash():
    x = CharParser("x")
    y = CharParser("y")

    assert hash(RepeatParser(x)) != hash(RepeatParser(y))
    assert hash(RepeatParser(x, _from=1, _to=100)) == hash(RepeatParser(x, _from=10, _to=100))
    assert hash(RepeatParser(x, _from=10, _to=10)) == hash(RepeatParser(x, _from=10, _to=100))
