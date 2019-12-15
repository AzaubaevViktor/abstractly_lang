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


@pytest.mark.parametrize('raw_line', (
    'abc',
    'a',
    'a' + 'b' * 100,
    '💻👏⏰🧠',
    'Lorem ipsum'
))
def test_simple_ok(raw_line):
    line = Line(raw_line)

    p = CharParser(raw_line[0])

    results = tuple(p.parse(line))

    assert len(results) == 1

    result = results[0]

    print(result)

    assert isinstance(result, ParseVariant)
    assert result.parser == p
    assert result.line == raw_line[1:]


@pytest.mark.parametrize('raw_line', (
    'xxxxxxx',
    '',
    '12912391239',
    '💻👏⏰🧠'
))
def test_simple_wrong(raw_line):
    line = Line(raw_line)

    a = CharParser('b')
    with pytest.raises(ParseError) as _e:
        tuple(a.parse(line))

    # TODO: Check exception object
