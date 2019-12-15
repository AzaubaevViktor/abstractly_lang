from itertools import product

import pytest

from line import Line
from parser.base import ParseError
from parser.char_parser import CharParser, CharParserInitError
from parser.parse_variant import ParseVariant


@pytest.fixture(scope='function')
def a():
    return CharParser('a')


class TestEq:
    params = ('a', 'x', '1', '✓', '🤔')

    @pytest.mark.parametrize('char', params)
    def test_eq(self, char):
        assert CharParser(char) == CharParser(char)

    @pytest.mark.parametrize('char', params)
    def test_same(self, char):
        p = CharParser(char)
        assert p == p

    @pytest.mark.parametrize('x,y', product(params, params))
    def test_eq_neq(self, x: str, y: str):
        if x == y:
            assert CharParser(x) == CharParser(y)
        else:
            assert CharParser(x) != CharParser(y)


@pytest.mark.parametrize('wrong_char', (
    'sadadsda', 'sfiewi30∅ff🤔', '💻👏⏰🧠'
))
def test_wrong_len(wrong_char):
    with pytest.raises(CharParserInitError) as _e:
        CharParser(wrong_char)

    assert wrong_char in str(_e.value)


def test_simple_ok():
    line = Line("abc")

    a = CharParser('a')

    results = tuple(a.parse(line))

    assert len(results) == 1

    result = results[0]

    assert isinstance(result, ParseVariant)
    assert result == a


def test_simple_wrong():
    line = Line("abc")

    a = CharParser('b')
    with pytest.raises(ParseError) as _e:
        tuple(a.parse(line))

    # TODO: Check exception object
