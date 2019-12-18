import pytest

from line import Line
from parser.base import BaseParser
from parser.logic.empty_parser import EmptyParser
from parser.parse_variant import ParseVariant


def test_eq():
    assert BaseParser() != EmptyParser()
    assert EmptyParser() == EmptyParser()
    ep = EmptyParser()
    assert ep == ep


@pytest.mark.parametrize("_line", (
    "saadsa",
    "",
    "a",
    "xxxxxx"
))
def test_empty(_line):
    parser = EmptyParser()
    line = Line(_line)

    results = list(parser.parse(line))
    assert len(results) == 1

    result = results[0]
    assert isinstance(result, ParseVariant)

    assert result.parser == EmptyParser()
    assert result.line == line

# TODO: From here, like:
#     {
#         EmptyParser(): {
#             'Hello World': [ParseVariant(EmptyParser(), Line('Hello Worlds'))],
#             '': [ParseVariant(EmptyParser(), Line(''))],
#             ...
#         }
#     }
