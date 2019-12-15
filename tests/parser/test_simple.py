from typing import List, Type

import pytest

from line import Line
from parser.base import ParseError, BaseParser
from parser.logic.char_parser import CharParser
from parser.parse_variant import ParseVariant

# TODO: Here! Enjoy.
#       Ессно можно добавлять свои тесты, если они кажутся адекватными
_items = {
    CharParser('x'): {
        'x': [ParseVariant(CharParser('x'), Line(""))],
        'xx': [ParseVariant(CharParser('x'), Line("x"))],
        "xy": [ParseVariant(CharParser('x'), Line("y"))],
        'y': ParseError
    },
    CharParser('y'): {
        'y': [ParseVariant(CharParser('y'), Line(''))]
    }
}


def items():
    for parser, _ in _items.items():
        for raw_line, results in _.items():
            yield parser, raw_line, results


def items_good():
    for *_, results in items():
        if isinstance(results, list):
            yield (*_, results)


def items_bad():
    for *_, results in items():
        if isinstance(results, type) and issubclass(results, ParseError):
            yield (*_, results)


def test_items():
    # Не делайте так никогда, пожалуйста
    assert len(tuple(items())) == len(tuple(items_good())) + len(tuple(items_bad())), \
        "Ошибка в _items. Проверяйте типы -- должны быть либо list, либо класс ошибки (не объект!)"


@pytest.mark.parametrize('p,raw_line,results', (
        *items_good(),
))
def test_good(p: BaseParser, raw_line: str, results: List[ParseVariant]):
    assert list(results) == list(p.parse(Line(raw_line)))


@pytest.mark.parametrize('p,raw_line,error', (
        *items_bad(),
))
def test_bad(p: BaseParser, raw_line: str, error: Type[ParseError]):
    line = Line(raw_line)
    with pytest.raises(error) as _e:
        tuple(p.parse(line))