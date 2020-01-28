from typing import Iterable

from line import Line
from parser.base import BaseParser, BaseParserError, ParseError
from parser.parse_variant import ParseVariant


class CharParserInitError(BaseParserError):
    pass


class CharParser(BaseParser):
    def __init__(self, s: str):
        self.s = s

    def __eq__(self, other: BaseParser):
        _result = super().__eq__(other)
        if _result is not None:
            return _result

        # Для того, чтобы автоподсветка не ругалась
        if not isinstance(other, CharParser):
            return False

        return self.s == other.s

    def __and__(self, other: BaseParser):
        if isinstance(other, CharParser):
            return CharParser(self.s + other.s)
        return super().__and__(other)

    def parse(self, line: Line) -> Iterable[ParseVariant]:
        if line and (line.startswith(self.s)):
            yield ParseVariant(CharParser(self.s), line[len(self.s):])
        else:
            raise ParseError("")

    def __repr__(self):
        return f"<{self.__class__.__name__}: {repr(self.s)}>"

    def __str__(self):
        return f"`{self.s}`"

    def __hash__(self):
        return hash(self.s)

    def __iter__(self):
        yield self

    @classmethod
    def line(cls, s: str) -> "CharParser":
        return CharParser(s)
