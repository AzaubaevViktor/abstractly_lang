from typing import Union

import pytest

from line import Line
from parser import AndParser
from parser import CharParser
from parser import EmptyParser
from parser import EndLineParser
from parser import FuncParser
from parser import KeyArgument
from parser.parse_variant import ParseVariant
from parser.common.simple import digit_parser

@pytest.fixture(scope='function')
def _digit_parser():
    return digit_parser


def p_to_num(result, sign: Union[CharParser, EmptyParser], number: AndParser):
    print(result, sign, number)
    num_str = "".join(p.ch for p in number)
    num = int(num_str)

    if sign:
        num = -num

    return num


@pytest.fixture(scope='function')
def number_parser(_digit_parser):
    # TODO: Реализовать всё, что подчёркнуто красным.
    #       Этот парсер трогать не нужно!
    return EndLineParser(FuncParser(
        KeyArgument('sign', CharParser('-')[:2]) & KeyArgument('number', _digit_parser[1:]),
        p_to_num
    ))


@pytest.mark.parametrize('raw_line', (
    '0', '1', '-10', '123123', '1234567890',
    '-1234567890'
))
def test_number(raw_line, number_parser):
    line = Line(raw_line)

    results = list(number_parser.parse(line))

    assert len(results) == 1
    result = results[0]

    assert isinstance(result, ParseVariant)
    assert isinstance(result.parser, EndLineParser)
    assert result.line == ''
    assert int(raw_line) == result.parser.calculate()
