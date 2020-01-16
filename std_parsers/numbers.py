import math
import operator
from typing import Union

from parser import CharParser, EmptyParser, AndParser, FuncParser, KeyArgument, OrParser, BasePriority, PriorityParser
from .common import digit, spaces
from .op_generators import generate_operation_2
from .variable import use_variables
from .functions import use_functions


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

number_expressions |= use_variables("@number", number_expressions)


number_expressions |= use_functions(number_expressions)
