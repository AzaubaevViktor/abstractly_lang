from parser import FuncParser, CharParser, KeyArgument
from std_parsers.common import spaces


def use_braces(base_expr):
    return FuncParser(
        CharParser('(') & spaces
        & KeyArgument(
            'e', base_expr
        ) & spaces & CharParser(')'),
        lambda *args, e: e
    )