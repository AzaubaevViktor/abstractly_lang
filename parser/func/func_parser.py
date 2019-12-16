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
            **{k: p.calculate()
               for k, p in self.parser.key_args().items()
            }
        )

    def __eq__(self, other: BaseParser):
        _result = super().__eq__(other)
        if _result is not None:
            return _result

        if not isinstance(other, self.__class__):
            return False

        return (self.parser == other.parser) and (self.func == other.func)

    def __str__(self):
        return f"{{{self.parser}}} => {self.func}"
