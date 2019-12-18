from itertools import product

import pytest

from line import Line
from parser.func.key_argument import KeyArgument
from parser.parse_variant import ParseVariant
from tests.parser.common.test_simple import items_good, items_good_empty_line


@pytest.mark.parametrize('alpha, add, key', (
    *product(
        items_good(),
        ("", "__"),
        ("test", "h🤔m")
    ),))
def test_key_arg(alpha, add, key):
    a_p, a_raw_line, a_results = alpha

    line = Line(f"{a_raw_line}{add}")

    p = KeyArgument(key, a_p)

    p_results = [
        ParseVariant(KeyArgument(key, pv.parser), Line(f"{pv.line}{add}"))
        for pv in a_results
    ]

    assert p_results == list(p.parse(line))


@pytest.mark.parametrize('alpha, beta, add, key_a, key_b', (
    *product(
        items_good_empty_line(),
        items_good(),
        ("", "__"),
        ("test", "h🤔m"),
        ("tost", "wo😲w")
    ),))
def test_2_key_arg(alpha, beta, add, key_a, key_b):
    a_p, a_raw_line, a_results = alpha
    b_p, b_raw_line, b_results = beta

    line = Line(f"{a_raw_line}{b_raw_line}{add}")

    p = KeyArgument(key_a, a_p) & KeyArgument(key_b, b_p)

    p_results = [
        ParseVariant(
            KeyArgument(key_a, pva.parser) & KeyArgument(key_b, pvb.parser),
            Line(f"{pvb.line}{add}")
        )
        for pva, pvb in product(a_results, b_results)
    ]

    p_actual = list(p.parse(line))
    assert p_results == p_actual


@pytest.mark.parametrize('alpha, beta, gamma, key_a, key_b', (
        *product(
            items_good_empty_line(),
            items_good(),
            items_good(),
            ("test", "h🤔m"),
            ("tost", "wo😲w")
        ),))
def test_keys_finder(alpha, beta, gamma, key_a, key_b):
    a_p, a_raw_line, a_results = alpha
    b_p, b_raw_line, b_results = beta
    c_p, c_raw_line, c_results = gamma

    p = KeyArgument(key_a, a_p) & KeyArgument(key_b, b_p) & c_p

    assert p.key_args() == {
        key_a: a_p,
        key_b: b_p
    }

    for pva, pvb, pvc in product(a_results, b_results, c_results):
        pr = KeyArgument(key_a, pva.parser) & KeyArgument(key_b, pvb.parser) & pvc.parser

        assert pr.key_args() == {
            key_a: pva.parser,
            key_b: pvb.parser
        }
