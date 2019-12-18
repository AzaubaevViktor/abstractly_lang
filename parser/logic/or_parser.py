from typing import Iterable, Sequence

from line import Line
from parser.base import BaseParser, ParseError
from parser.logic._multi_parser import MultiParser
from parser.parse_variant import ParseVariant


class OrParserError(ParseError):
    def __init__(self, msg, errors):
        super().__init__(msg)
        self.errors = errors


def uniques(f):
    def _(*args, **kwargs):
        items = []

        for item in f(*args, **kwargs):

            if item not in items:
                items.append(item)
                yield item
    return _


class OrParser(MultiParser):
    STR_SYM = '|'
    @uniques
    def parse(self, line: Line) -> Iterable[ParseVariant]:
        errors = []

        is_found = False

        for parser in self._rearrange(self.parsers):
            # print(parser, line)
            try:
                yield from parser.parse(line)
            except ParseError as e:
                # TODO: Add context to e
                errors.append(e)
            else:
                is_found = True

        if not is_found:
            raise OrParserError("No one parser", errors)

    def _rearrange(self, parsers: Sequence[BaseParser]):
        srt = sorted(parsers, key=self._search)
        # print(srt)
        return srt

    def __hash__(self):
        raw_hashes = sorted(map(hash, self.parsers))
        s_to_hash = '-'.join(map(str, raw_hashes))
        return hash(s_to_hash)

    def __ior__(self, other: BaseParser):
        if isinstance(other, OrParser):
            self.parsers = (*self.parsers, *other.parsers)
        else:
            self.parsers = (*self.parsers, other)

        return self
