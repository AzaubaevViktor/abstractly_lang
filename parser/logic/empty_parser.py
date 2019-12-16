from typing import Iterable

from line import Line
from parser.base import BaseParser
from parser.parse_variant import ParseVariant


class EmptyParser(BaseParser):
    def parse(self, line: Line) -> Iterable[ParseVariant]:
        yield ParseVariant(EmptyParser(), line[:])

    def __repr__(self):
        return "∅"

    def __eq__(self, other: BaseParser):
        _result = super().__eq__(other)
        if _result is not None:
            return _result

        return isinstance(other, EmptyParser)

    def __bool__(self):
        return False
