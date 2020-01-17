from typing import Iterable

from line import Line
from parser.base import BaseParser, ParseError
from parser.logic.empty_parser import EmptyParser
from parser.parse_variant import ParseVariant


class RepeatParserValuesError(ParseError):
    pass


class RepeatParserError(ParseError):
    pass


class RepeatParser(BaseParser):
    def __init__(self, p: BaseParser, _from=None, _to=None):
        self.p = p
        self._from = 0 if _from is None else _from
        self._to = float("+inf") if _to is None else _to

        if self._from >= self._to:
            raise RepeatParserValuesError(
                f"Wrong values: `from`: ({self._from}) must be less than to ({self._to})"
            )

    def parse(self, line: Line) -> Iterable[ParseVariant]:
        level = 0
        variants = [ParseVariant(EmptyParser(), line)]
        is_found = False

        while True:
            if self._from <= level < self._to:
                yield from variants
                is_found = True

            new_variants = []

            for variant in variants:
                try:
                    for result in self.p.parse(variant.line):
                        new_variants.append(
                            ParseVariant(variant.parser & result.parser, result.line)
                        )
                except ParseError:
                    pass

            if not new_variants:
                break

            variants = new_variants
            level += 1

        if not is_found:
            raise RepeatParserError("Not found anything")

    def __repr__(self):
        return f"<RepeatParser {self._from}:{self._to} of {self.p}>"

    def __hash__(self):
        return hash(self.__class__) * hash(self.p) * hash(self._from) * hash(self._to)

    def __eq__(self, other: BaseParser):
        _result = super().__eq__(other)
        if _result is not None:
            return _result

        if not isinstance(other, RepeatParser):
            return False

        return self.p == other.p and self._from == other._from and self._to == other._to

