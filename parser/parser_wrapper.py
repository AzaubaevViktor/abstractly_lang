from typing import Iterable, Any

from line import Line
from parser.base import BaseParser
from parser.parse_variant import ParseVariant


class WrapperParser(BaseParser):
    def __init__(self, parser: BaseParser):
        self.parser = parser

    def _wrap(self, parser: BaseParser):
        raise NotImplementedError()

    def parse(self, line: Line) -> Iterable[ParseVariant]:
        for variant in self.parser.parse(line):
            yield ParseVariant(
                self._wrap(variant.parser),
                variant.line
            )
        # TODO: try + except + context

    def calculate(self) -> Any:
        return self.parser.calculate()

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.parser}>"
