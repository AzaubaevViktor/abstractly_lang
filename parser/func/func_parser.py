from typing import Iterable, Callable, Any

from line import Line
from parser.base import BaseParser
from parser.parse_variant import ParseVariant
from parser.parser_wrapper import WrapperParser


class FuncParser(WrapperParser):
    def __init__(self, parser: BaseParser, func: Callable):
        super().__init__(parser)
        self.func = func

    def _wrap(self, parser: BaseParser):
        return FuncParser(parser, self.func)

    def calculate(self) -> Any:
        return self.func(
            self.parser,
            **self.parser.key_args()
        )
