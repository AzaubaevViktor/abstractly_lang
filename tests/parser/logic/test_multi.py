from parser.logic.and_parser import AndParser
from parser.logic.char_parser import CharParser


def test_and_combine():
    x = CharParser('x')
    y = CharParser('y')
    z = CharParser('z')

    assert (x & y) & z == x & (y & z)


def test_or_combine():
    x = CharParser('x')
    y = CharParser('y')
    z = CharParser('z')

    assert (x | y) | z == x | (y | z)


def test_and_or_combine():
    x = CharParser('x')
    y = CharParser('y')
    z = CharParser('z')

    assert (x & y) | z != x & (y | z)
