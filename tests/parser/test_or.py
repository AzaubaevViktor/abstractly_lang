from itertools import product
from typing import Callable, List, Type

import pytest

from line import Line
from parser.base import BaseParser, ParseError
from parser.logic.char_parser import CharParser
from parser.logic.or_parser import OrParser
from parser.parse_variant import ParseVariant

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


def _or(x, y):
    x | y


def _orp(x, y):
    return OrParser(x, y)


@pytest.mark.parametrize('alpha, beta, op, add', (
        *product(items_good(), items(), (
                _or,
                _orp
        ), ("", "___")),
))
def test_or(alpha, beta, op, add):
    a_p, a_raw_line, a_results = alpha
    b_p, b_raw_line, b_results = beta

    p = op(a_p, b_p)
    line = Line(f"{a_raw_line}{b_raw_line}{add}")

    p_results = [
        ParseVariant(pv.parser, Line(f"{pv.line}{b_raw_line}{add}"))
        for pv in a_results
    ]

    assert p_results == list(p.parse(line))
