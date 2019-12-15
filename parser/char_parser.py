from typing import Iterable

from line import Line
from parser.base import BaseParser, BaseParserError
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
        pass
