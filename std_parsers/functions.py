import math

from parser import FuncParser, KeyArgument, CharParser, PriorityParser, DictParser
from parser.base import BaseParser
from std_parsers.common import var_symbol, spaces
from std_parsers.variable import variables

variables['@factorial'] = math.factorial
variables['vars_keys'] = lambda *args: variables.keys()


def use_functions(base_expr: BaseParser, priority=None):
    def _f(*result, f, arg):
        return f(arg)

    parser = FuncParser(
        KeyArgument('f', DictParser(variables)) & spaces
        & CharParser('(') & spaces
        & KeyArgument('arg', base_expr) & spaces
        & CharParser(')'),
        _f
    )

    if priority:
        parser = PriorityParser(parser, priority)

    return parser
