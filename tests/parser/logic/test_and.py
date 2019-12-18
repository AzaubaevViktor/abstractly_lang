from itertools import product

import pytest

from line import Line
from parser.logic.and_parser import AndParser
from parser.parse_variant import ParseVariant
from tests.parser.common.test_simple import items_good, items_good_empty_line


def _and(*parsers):
    ps = parsers[0]
    for p in parsers[1:]:
        ps = ps & p
    return ps


def _andp(*parsers):
    return AndParser(*parsers)


@pytest.mark.parametrize('alpha, beta, op, add', (
    *product(
        items_good_empty_line(),
        items_good(),
        (_and, _andp),
        ("", "___")
),))
def test_and_2(alpha, beta, op, add):
    a_p, a_raw_line, a_results = alpha
    b_p, b_raw_line, b_results = beta

    p = op(a_p, b_p)
    line = Line(f"{a_raw_line}{b_raw_line}{add}")
    print()
    print("⚠️ Line:", line)

    p_results = [
        ParseVariant(
            op(pva.parser, pvb.parser),
            Line(f"{pvb.line}{add}")
        )
        for pva, pvb in product(a_results, b_results)
    ]

    assert p_results == list(p.parse(line))


@pytest.mark.parametrize('alpha, beta, gamma, op, add', (
    *product(
        items_good_empty_line(),
        items_good_empty_line(),
        items_good(),
        (_and, _andp),
        ("", "___")
),))
def test_and_3(alpha, beta, gamma, op, add):
    a_p, a_raw_line, a_results = alpha
    b_p, b_raw_line, b_results = beta
    c_p, c_raw_line, c_results = gamma

    p = op(a_p, b_p, c_p)
    line = Line(f"{a_raw_line}{b_raw_line}{c_raw_line}{add}")
    print()
    print("⚠️ Line:", line)

    p_results = [
        ParseVariant(
            op(pva.parser, pvb.parser, pvc.parser),
            Line(f"{pvc.line}{add}")
        )
        for pva, pvb, pvc in product(a_results, b_results, c_results)
    ]

    assert p_results == list(p.parse(line))
