from typing import Iterable, Callable, Any

from line import Line
from parser.base import BaseParser
from parser.parse_variant import ParseVariant


class FuncParser(BaseParser):
    def __init__(self, parser: BaseParser, func: Callable):
        self.parser = parser
        self.func = func

    def parse(self, line: Line) -> Iterable[ParseVariant]:
        for result in self.parser.parse(line):
            yield ParseVariant(
                FuncParser(result.parser, self.func),
                result.line
            )

    def calculate(self) -> Any:
        return self.func(
            self.parser,
            **self.parser.key_args()
        )
