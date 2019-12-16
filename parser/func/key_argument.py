from typing import Iterable

from line import Line
from parser.base import BaseParser
from parser.parse_variant import ParseVariant


class KeyArgument(BaseParser):
    def __init__(self, key: str, parser: BaseParser):
        self.key = key
        self.parser = parser

    def parse(self, line: Line) -> Iterable[ParseVariant]:
        for variant in self.parser.parse(line):
            yield ParseVariant(
                KeyArgument(self.key, variant.parser),
                variant.line
            )

    def __eq__(self, other: BaseParser):
        _result = super().__eq__(other)
        if _result is not None:
            return _result

        if not isinstance(other, self.__class__):
            return False

        return (self.parser == other.parser) and (self.key == other.key)
