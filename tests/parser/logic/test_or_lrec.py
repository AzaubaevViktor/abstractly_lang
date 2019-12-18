"""
Разбор леворекурсивных правил. Пока разворачиваем их руками, чё делать
"""
import pytest

from line import Line
from parser.logic.char_parser import CharParser
from parser.logic.or_parser import OrParser


def test_or_set():
    y = x = OrParser(CharParser("x"))
    x |= CharParser('y')

    assert y is x

    assert x == CharParser('x') | CharParser('y')


@pytest.mark.parametrize('raw_line', (
    'x',
    'xy'
))
def test_or_lrec(raw_line):
    line = Line(raw_line)
    x = OrParser(CharParser('x'))
    x |= x & CharParser('y')

    results = list(x.parse(line))
    assert len(results) == len(raw_line)

    for result in results:
        print(result)
