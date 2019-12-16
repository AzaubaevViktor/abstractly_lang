import pytest

from line import Line
from parser.func.key_argument import KeyArgument
from parser.logic.char_parser import CharParser


def sym_to_num(*args, **kwargs):
    print(args, kwargs)

    assert 'symbol' in kwargs
    assert isinstance(kwargs['symbols'], CharParser)

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

    assert isinstance(result, FuncParser)
    assert int(raw_line) == result.calculate()
