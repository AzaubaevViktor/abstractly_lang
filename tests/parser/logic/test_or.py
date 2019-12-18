from itertools import product

import pytest

from line import Line
from parser import OrParser
from parser.parse_variant import ParseVariant
from tests.parser.common.test_simple import items, items_good


def _or(x, y):
    return x | y


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
