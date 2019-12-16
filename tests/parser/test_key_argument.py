from itertools import product

import pytest

from line import Line
from parser.func.key_argument import KeyArgument
from parser.parse_variant import ParseVariant
from tests.parser.test_simple import items_good


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
