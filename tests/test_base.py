from parser import CharParser, AndParser, OrParser


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
