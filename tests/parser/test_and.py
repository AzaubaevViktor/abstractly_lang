from itertools import product

import pytest

from line import Line
from parser.logic.and_parser import AndParser
from parser.parse_variant import ParseVariant
from tests.parser.test_simple import items_good, items


def _and(x, y):
    return x & y


def _andp(x, y):
    return AndParser(x, y)


def items_good_empty_line():
    for parser, raw_line, results in items_good():
        results = list(results)
        for result in results[:]:
            if result.line != Line(""):
                results.remove(result)

        if results:
            yield parser, raw_line, results


@pytest.mark.parametrize('alpha, beta, op, add', (
        *product(items_good_empty_line(), items_good(), (
                _and,
                _andp
        ), ("", "___")),
))
def test_and(alpha, beta, op, add):
    a_p, a_raw_line, a_results = alpha
    b_p, b_raw_line, b_results = beta

    p = op(a_p, b_p)
    line = Line(f"{a_raw_line}{b_raw_line}{add}")
    print()
    print("⚠️ Line:", line)

    p_results = [
        ParseVariant(
            op(pva.parser, pvb.parser),
            Line(f"{pva.line}{pvb.line}{add}")
        )
        for pva, pvb in product(a_results, b_results)
    ]

    assert p_results == list(p.parse(line))
