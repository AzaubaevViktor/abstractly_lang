from itertools import product

import pytest

from line import Line
from parser.base import ParseError
from parser.logic.and_parser import AndParser
from parser.logic.empty_parser import EmptyParser
from parser.logic.repeat_parser import RepeatParser
from parser.parse_variant import ParseVariant
from tests.parser.common.test_simple import items_good_empty_line


def _rep(p, f, t):
    return p[f:t]


def _repp(p, f, t):
    return RepeatParser(p, f, t)


_max_items = 10


@pytest.mark.parametrize('alpha, op, raw_f, raw_t, add, count', (
    *product(
        items_good_empty_line(),
        (
                _rep,
                _repp,
        ),
        (None, 1, 2, 3),
        (None, 1, 2, 3, 5),
        ("", "__"),
        range(_max_items)
), ))
def test_repeat(alpha, op, raw_f, raw_t, add, count):
    a_p, a_raw_line, a_results = alpha

    f = 0 if raw_f is None else raw_f
    t = _max_items if raw_t is None else raw_t

    if f >= t:
        with pytest.raises(ParseError):
            op(a_p, raw_f, raw_t)
        return

    p = op(a_p, raw_f, raw_t)

    line = Line(f"{a_raw_line}" * count + f"{add}")

    if count < f:
        with pytest.raises(ParseError):
            list(p.parse(line))

    elif f <= count:
        p_results = []

        for i in range(f, min(t, count + 1)):
            _to = min(t, i)

            if count > i:
                raw_lines = f"{a_raw_line}" * (count - i)
            else:
                raw_lines = ""

            line_less = Line(raw_lines + add)

            _parsers = [pv.parser for pv in a_results]
            if i:
                p_result = [AndParser(*pss) for pss in product(*(_parsers for _ in range(_to)))]
            else:
                p_result = [EmptyParser()]

            p_results += [
                ParseVariant(parser, line_less)
                for parser in p_result
            ]
        # Check
        assert p_results == list(p.parse(line))
    else:
        raise NotImplementedError()
