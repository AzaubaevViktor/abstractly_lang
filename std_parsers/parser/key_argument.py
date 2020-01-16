from parser import FuncParser, PriorityParser, KeyArgument, CharParser
from parser.base import BaseParser
from .base import ParserPriority
from ..common import var_name, spaces


def use_key_argument(base_expr: BaseParser):
    _p = (KeyArgument('name', var_name) & spaces
          & CharParser(":") & spaces
          & KeyArgument('parser', base_expr)
          )

    def _f(*result, name: str, parser: BaseParser):
        print(f"KeyArgument generator: {name}, {parser}")
        return KeyArgument(name, parser)

    return PriorityParser(FuncParser(
        _p,
        _f
    ), ParserPriority(100))
