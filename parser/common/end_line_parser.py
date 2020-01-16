from typing import Iterable

from line import Line
from parser.base import BaseParser, ParseError
from parser.parse_variant import ParseVariant
from parser.parser_wrapper import WrapperParser


class NotFoundEndLineError(ParseError):
    pass


class EndLineParser(WrapperParser):
    def _wrap(self, parser: BaseParser):
        return EndLineParser(parser)

    def parse(self, line: Line) -> Iterable[ParseVariant]:
        is_found = False
        wrong_variants = []

        for variant in super().parse(line):
            if variant.line == '':
                is_found = True
                yield variant
            else:
                wrong_variants.append(variant)

        if not is_found:
            raise NotFoundEndLineError(
                "Not found variant with end line",
                line=line,
                parser=self,
                wrong_variants=wrong_variants
            )

    def __eq__(self, other):
        _result = super().__eq__(other)
        if _result is not None:
            return _result

        if not isinstance(other, self.__class__):
            return False

        return self.parser == other.parser

    def __str__(self):
        return f"{self.parser} (\\0)"
