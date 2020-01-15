import math
import operator
from typing import Union, Callable, Dict, Any, Optional, List

from parser import CharParser, EmptyParser, AndParser, FuncParser, KeyArgument, OrParser, BasePriority, PriorityParser, \
    DictParser
from parser.base import BaseParser
from .common import digit, spaces


class NumberPriority(BasePriority):
    pass


number_expressions = OrParser()


def parsed_to_number(*args,
                     sign: Union[CharParser, EmptyParser],
                     digits: AndParser
                     ):
    num_str = "".join(p.ch for p in digits)

    num = int(num_str)

    if sign:
        num = -num

    return num


number = FuncParser(
    KeyArgument(
        'sign',
        CharParser('-')[:2]
    )
    & KeyArgument(
        'digits',
        digit[1:]
    ),
    parsed_to_number
)

number_expressions |= number


def generate_operation_2(
        base_expr: BaseParser,
        ops: Dict[str, Callable[[Any, Any], Any]],
        priority: Optional[BasePriority]
):
    # Создаёт операцию от двух переменных с оператором symbol

    def _func_wrapper(*args, a, op: Callable, b):
        return op(a, b)

    parser = FuncParser(
        KeyArgument('a', base_expr) & spaces
        & KeyArgument('op', DictParser(ops)) & spaces
        & KeyArgument('b', base_expr),
        _func_wrapper
    )
    if priority:
        parser = PriorityParser(parser, priority)

    return parser


number_expressions |= generate_operation_2(
    number_expressions, {
        "-": operator.sub,
        "+": operator.add
    },
    NumberPriority(10)
)

number_expressions |= generate_operation_2(
    number_expressions, {
        "*": operator.mul,
        "/": operator.truediv
    },
    NumberPriority(20)
)


# Braces

number_expressions |= \
    FuncParser(
        CharParser('(') & spaces
        & KeyArgument(
            'e', number_expressions
        ) & spaces & CharParser(')'),
        lambda *args, e: e
    )


# Factorial


number_expressions |= PriorityParser(
    FuncParser(
        KeyArgument(
            'e', number_expressions
        ) & spaces & CharParser('!'),
        lambda *args, e: math.factorial(e)
    ),
    NumberPriority(50)
)


# Power

number_expressions |= generate_operation_2(
    number_expressions, {
        '**': math.pow
    },
    NumberPriority(40)
)


# Variables

variables = {
    'hello': 'world!',
    'pi': math.pi
}

variables_parser = DictParser(variables)
number_expressions |= variables_parser


def _set_var_func(*result, name, value: Any):
    if isinstance(name, list):
        name = "".join(x.ch for x in name)
    else:
        name = name.ch

    global variables_parser
    print(name, value)
    variables_parser.d[name] = value

    return value


symbol = OrParser(*(CharParser(x) for x in "qwertyuiopasdfghjklzxcvbnm"))


number_expressions |= FuncParser(
    KeyArgument('name', symbol[1:]) & spaces
    & CharParser('=') & spaces
    & KeyArgument('value', number_expressions),
    _set_var_func
)
