from itertools import product

import pytest

from line import Line
from parser.base import ParseError
from parser import EndLineParser
from parser.parse_variant import ParseVariant
from tests.parser.common.test_simple import items_good


@pytest.mark.parametrize('alpha, add', (
    *product(
        items_good(),
        ("", "___")
),))
def test_end_line(alpha, add):
    a_p, a_raw_line, a_results = alpha

    p = EndLineParser(a_p)

    line = Line(f"{a_raw_line}{add}")

    p_results = [
        ParseVariant(
            EndLineParser(pva.parser),
            Line(f"{pva.line}{add}")
        )
        for pva in a_results
    ]

    p_results = [result for result in p_results if result.line == '']

    if p_results:
        assert p_results == list(p.parse(line))
    else:
        with pytest.raises(ParseError):
            list(p.parse(line))
