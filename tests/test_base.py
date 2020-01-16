from parser import CharParser, AndParser, OrParser, KeyArgument, FuncParser


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
