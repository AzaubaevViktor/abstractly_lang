from typing import Iterable, Any

from line import Line
from parser.base import BaseParser
from parser.parse_variant import ParseVariant


class WrapperParser(BaseParser):
    def __init__(self, parser: BaseParser):
        self.parser: BaseParser = parser

    def _wrap(self, parser: BaseParser):
        raise NotImplementedError()

    def parse(self, line: Line) -> Iterable[ParseVariant]:
        for variant in self.parser.parse(line):
            yield ParseVariant(
                self._wrap(variant.parser),
                variant.line
            )
        # TODO: try + except + context

    def calculate(self, executor: 'Executor') -> Any:
        return self.parser.calculate(executor)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.parser}>"

    def __iter__(self):
        yield self
        yield self.parser
        yield from self.parser

    def __ior__(self, other: BaseParser):
        self.parser |= other
        return self
