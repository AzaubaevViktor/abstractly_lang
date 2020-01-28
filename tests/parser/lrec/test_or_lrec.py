"""
Разбор леворекурсивных правил. Пока разворачиваем их руками, чё делать
"""
from typing import List

import pytest

from line import Line
from parser import CharParser, EndLineParser, AndParser, ParseVariant
from parser import OrParser
from parser.base import ParseError


def test_or_set():
    y = x = OrParser(CharParser("x"))
    x |= CharParser('y')

    assert y is x

    assert x == CharParser('x') | CharParser('y')


@pytest.mark.parametrize('raw_line', (
    'x',
    'xy',
    'xyyyy'
))
def test_or_lrec(raw_line):
    line = Line(raw_line)
    x = OrParser(CharParser('x'))
    x |= x & CharParser('y')

    results = list(x.parse(line))
    assert len(results) == len(raw_line)

    for result in results:
        print(result)


@pytest.mark.parametrize('raw_line', (
    'x', 'z', 'xy',  'zy', 'xyy', 'zyyy',
))
def test_deep_lrec_good(raw_line: str):
    line = Line(raw_line)

    x = OrParser(CharParser('x'))
    a = x & CharParser('y')  # X `y`
    b = a | CharParser('z')  # X 'y' | z
    x |= b  # X = x | z | X 'y'

    _x = EndLineParser(x)

    results = list(_x.parse(line))

    assert len(results) == 1

    result = results[0]

    assert isinstance(result.parser, EndLineParser)
    pr = result.parser.parser
    if len(raw_line) == 1:
        assert isinstance(pr, CharParser)
        assert pr.s == raw_line
    else:
        assert isinstance(pr, AndParser)
        assert len(pr.parsers) == len(raw_line)


@pytest.mark.parametrize('raw_line', (
    'xz', 'xx', 'y', 'zyyyx',
))
def test_deep_lrec_wrong(raw_line: str):
    line = Line(raw_line)

    x = OrParser(CharParser('x'))
    a = x & CharParser('y')  # X `y`
    b = a | CharParser('z')  # X 'y' | z
    x |= b  # X = x | z | X 'y'

    _x = EndLineParser(x)

    with pytest.raises(ParseError):
        list(_x.parse(line))


def test_simple_lrec():
    x = OrParser(CharParser('x'))
    x |= x & CharParser('y')

    results: List[ParseVariant] = list(x.parse(Line('xyy')))

    assert results == [
        ParseVariant(CharParser('x'), Line('yy')),
        ParseVariant(CharParser('x') & CharParser('y'), Line('y')),
        ParseVariant(CharParser('x') & CharParser('y') & CharParser('y'), Line(''))
    ]
