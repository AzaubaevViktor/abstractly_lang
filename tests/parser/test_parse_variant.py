from line import Line
from parser.logic.char_parser import CharParser
from parser.parse_variant import ParseVariant


def test_parse_variant():
    assert ParseVariant(
        CharParser('x'),
        Line("yy")
    ) == ParseVariant(
        CharParser('x'),
        Line("yy")
    )

    assert ParseVariant(
        CharParser('x'),
        Line("yy")
    ) == ParseVariant(
        CharParser('x'),
        Line("yy")[:]
    )

    assert ParseVariant(
        CharParser('x'),
        Line("yy")
    ) == ParseVariant(
        CharParser('x'),
        Line("yyyy")[1:][1:]
    )
