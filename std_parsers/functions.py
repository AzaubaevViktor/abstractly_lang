import math

from parser import FuncParser, KeyArgument, CharParser, PriorityParser, DictParser, EmptyParser, OrParser
from parser.base import BaseParser
from std_parsers.common import spaces
from std_parsers.variable import variables

variables['@factorial'] = math.factorial
variables['@power'] = math.pow
variables['_return_hello'] = lambda: "hello"
variables['vars_keys'] = lambda: variables.keys()


def use_functions(base_expr: BaseParser, priority=None):
    def _f(*result, f, arg=None, arg_left=None, arg_right=None):
        print(arg, ';', arg_left, '<->', arg_right)
        if arg:
            return f(arg)
        elif arg_left and arg_right:
            return f(arg_left, arg_right)
        else:
            return f()

    _arg_p = OrParser()
    _arg_p |= EmptyParser()
    _arg_p |= KeyArgument('arg', base_expr)
    _arg_p |= KeyArgument('arg_left', _arg_p) & spaces & CharParser(',') & spaces & KeyArgument('arg_right', _arg_p)

    parser = FuncParser(
        KeyArgument('f', DictParser(variables)) & spaces
        & CharParser('(') & spaces
        & _arg_p & spaces
        & CharParser(')'),
        _f
    )

    if priority:
        parser = PriorityParser(parser, priority)

    return parser
