from typing import Optional, Union

import pytest

from line import Line
from parser.common.end_line_parser import EndLineParser
from parser.func.func_parser import FuncParser
from parser.func.key_argument import KeyArgument
from parser.logic.and_parser import AndParser
from parser.logic.char_parser import CharParser
from parser.logic.empty_parser import EmptyParser
from parser.parse_variant import ParseVariant


@pytest.fixture(scope='function')
def _digit_parser():
    return CharParser('0') \
                | CharParser('1') \
                | CharParser('2') \
                | CharParser('3') \
                | CharParser('4') \
                | CharParser('5') \
                | CharParser('6') \
                | CharParser('7') \
                | CharParser('8') \
                | CharParser('9')


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


@pytest.mark.parametrize("raw_line", (
    f"{ps}__" for ps in map(str, range(10))
))
def test_digit(_digit_parser, raw_line):
    line = Line(raw_line)

    results = tuple(_digit_parser.parse(line))
    assert len(results) == 1
    result = results[0]

    assert isinstance(result, ParseVariant)
    assert result.parser == CharParser(raw_line[0])
    assert result.line == line[1:]


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
