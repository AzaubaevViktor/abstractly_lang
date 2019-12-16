from typing import Iterable

from line import Line
from parser.base import BaseParser, ParseError
from parser.parse_variant import ParseVariant


class RepeatParserValuesError(ParseError):
    pass


class RepeatParser(BaseParser):
    def __init__(self, p, _from=None, _to=None):
        self.p = p
        self._from = 0 if _from is None else _from
        self._to = float("+inf") if _to is None else _to

        if self._from >= self._to:
            raise RepeatParserValuesError(
                f"Wrong values: `from`: ({self._from}) must be less than to ({self._to})"
            )

    def parse(self, line: Line) -> Iterable[ParseVariant]:
        if False:
            yield None
