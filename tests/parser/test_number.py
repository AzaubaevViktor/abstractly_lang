import pytest

from line import Line
from parser.logic.char_parser import CharParser
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


@pytest.fixture(scope='function')
def number_parser(_digit_parser):
    return ActionParser(
        KeyArgument('sign', OptionalParser('-'))
            & spaces_parser
            & KeyArgument('number', NonZeroParser(_digit_parser)),
        p_to_num
    )


@pytest.mark.parametrize("raw_line", (
    f"{ps}__" for ps in map(str, range(10))
))
def test_digit(_digit_parser, raw_line):
    line = Line(raw_line)

    results = _digit_parser.parse(line)
    assert len(results) == 1
    result = results[0]

    assert isinstance(result, ParseVariant)
    assert result.parser == CharParser(raw_line)
    assert result.line == line[1:]
