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

    def parse(self, line: Line) -> Iterable[ParseVariant]:
        pass
