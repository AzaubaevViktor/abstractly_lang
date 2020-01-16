import pytest

from line import Line
from parser import FuncParser
from parser import KeyArgument
from parser import CharParser
from parser.parse_variant import ParseVariant


def sym_to_num(*args, **kwargs):
    print(args, kwargs)

    assert 'symbol' in kwargs
    assert isinstance(kwargs['symbol'], CharParser)

    return int(kwargs['symbol'].ch)


@pytest.mark.parametrize('raw_line', (
    '0', '1'
))
def test_action_parser(raw_line):
    line = Line(raw_line)

    dig = CharParser('0') | CharParser('1')
    kax = KeyArgument('symbol', dig)

    acx = FuncParser(kax, sym_to_num)

    results = list(acx.parse(line))

    assert len(results) == 1
    result = results[0]

    assert isinstance(result, ParseVariant)
    assert isinstance(result.parser, FuncParser)
    assert result.line == ''
    assert int(raw_line) == result.parser.calculate(None)
