from typing import Iterable

from line import Line
from parser.base import BaseParser, BaseParserError, ParseError
from parser.parse_variant import ParseVariant


class CharParserInitError(BaseParserError):
    pass


class CharParser(BaseParser):
    def __init__(self, ch: str):
        if len(ch) != 1:
            raise CharParserInitError(
                "Value must be length 1, not "
                f"{len(ch)} {repr(ch)}"
            )

        self.ch = ch

    def __eq__(self, other: BaseParser):
        _result = super().__eq__(other)
        if _result is not None:
            return _result

        # Для того, чтобы автоподсветка не ругалась
        if not isinstance(other, CharParser):
            return False

        return self.ch == other.ch

    def parse(self, line: Line) -> Iterable[ParseVariant]:
        if len(line) and (line[0] == self.ch):
            yield ParseVariant(CharParser(self.ch), line[1:])
        else:
            raise ParseError(f"Expect {repr(self.ch)}, but {repr(line[0]) if len(line) else line}")

    def __str__(self):
        return f"<{self.__class__.__name__}: {repr(self.ch)}>"
