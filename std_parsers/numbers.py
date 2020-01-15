import math
import operator
from typing import Union, Callable, Dict, Any, Optional, List

from parser import CharParser, EmptyParser, AndParser, FuncParser, KeyArgument, OrParser, BasePriority, PriorityParser
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
        CharParser('-')[:1]
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

    ops_key_parsers = {
        CharParser.line(k): v
        for k, v in ops.items()
    }

    def _func_wrapper(*args, a, op: Union[CharParser, List[CharParser]], b):
        if isinstance(op, list):
            op = AndParser(*op)
        return ops_key_parsers[op](a, b)

    _func_wrapper.__name__ = f"op_for_{'_'.join(ops.keys())}"

    op_parser = OrParser(*(CharParser.line(k) for k in ops.keys()))

    parser = FuncParser(
        KeyArgument('a', base_expr) & spaces
        & KeyArgument('op', op_parser) & spaces
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
        "/": operator.floordiv
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
