from parser.base import BaseParser
from parser.logic.empty_parser import EmptyParser


class MultiParser(BaseParser):
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
