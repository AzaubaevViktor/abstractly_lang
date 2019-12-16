from typing import Dict

from parser.base import BaseParser
from parser.func.key_argument import KeyArgument
from parser.logic.empty_parser import EmptyParser


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

    def __eq__(self, other: BaseParser):
        _result = super().__eq__(other)
        if _result is not None:
            return _result

        if not isinstance(other, self.__class__):
            return False

        return self.parsers == other.parsers

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
        parsers_str = (str(parser) if not self._search(parser) else "..." for parser in self.parsers)
        return "(" + f" {self.STR_SYM} ".join(parsers_str) + ")"
