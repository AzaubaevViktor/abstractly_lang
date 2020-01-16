from typing import Dict, List, Any

from parser.base import BaseParser
from parser.func.key_argument import KeyArgument
from parser.logic.empty_parser import EmptyParser


def unique(f):
    def _(*args, **kwargs):
        memo = set()
        for item in f(*args, **kwargs):
            if item not in memo:
                memo.add(item)
                yield item

    return _


class MultiParser(BaseParser):
    STR_SYM = None

    def __init__(self, *parsers):
        _parsers = []

        for parser in parsers:
            if isinstance(parser, self.__class__):
                _parsers.extend(parser.parsers)
            else:
                _parsers.append(parser)

        self.parsers = tuple(p for p in _parsers if not isinstance(p, EmptyParser))
        self._iter_deep = False
        self._hash_deep = False
        self._str_deep = 0

    def __eq__(self, other: BaseParser):
        _result = super().__eq__(other)
        if _result is not None:
            return _result

        if not isinstance(other, self.__class__):
            return False

        return self.parsers == other.parsers

    def __hash__(self):
        if self._hash_deep:
            return hash(-1)

        self._hash_deep = True
        raw_hashes = sorted(map(hash, self.parsers))
        s_to_hash = self.STR_SYM + '-'.join(map(str, raw_hashes))
        _calculated_hash = hash(s_to_hash)
        self._hash_deep = False
        return _calculated_hash

    def key_args(self) -> Dict[str, BaseParser]:
        _kas = {}
        for parser in self.parsers:
            if isinstance(parser, KeyArgument):
                _kas[parser.key] = parser.parser

        return _kas

    def __repr__(self):
        parsers_str = (repr(parser) if not self._search(parser) else "..." for parser in self.parsers)
        return f"<{self.__class__.__name__}: {'; '.join(parsers_str)}>"

    def __str__(self):
        if self._str_deep:
            return "🔃"
        self._str_deep = True
        parsers_str = (str(parser) if not self._search(parser) else "..." for parser in self.parsers)
        s = "(" + f" {self.STR_SYM} ".join(parsers_str) + ")"
        self._str_deep = False
        return s

    def calculate(self) -> List[Any]:
        return list(p.calculate() for p in self.parsers)

    def __iter__(self):
        if not self._iter_deep:
            self._iter_deep = True
            yield self
            yield from self.parsers
            for parser in self.parsers:
                yield from parser
            self._iter_deep = False
