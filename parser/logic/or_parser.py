from collections import defaultdict
from typing import Iterable, Sequence, Dict, List

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

    def __init__(self, *parsers: BaseParser):
        super().__init__(*parsers)
        self.results: Dict[Line, List[ParseVariant]] = defaultdict(list)
        self.deep: Dict[Line, int] = defaultdict(int)

    def parse(self, line: Line) -> Iterable[ParseVariant]:
        print("PARSE   :", self, line)
        print("DEEP    :", self.deep[line])
        print("RESULTS :", self.results[line])

        yield from self.results[line]

        if self.deep[line] != 0:
            return

        self.deep[line] += 1

        while True:
            prev_results_count = len(self.results[line])

            for parser in self.parsers:
                try:
                    for item in parser.parse(line):
                        if item not in self.results[line]:
                            self.results[line].append(item)
                            yield item
                except ParseError:
                    pass

            if prev_results_count == len(self.results[line]):
                break

        self.deep[line] -= 1

    @uniques
    def _parse(self, line: Line) -> Iterable[ParseVariant]:
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
