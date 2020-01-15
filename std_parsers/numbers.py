import operator
from typing import Union, Callable, Dict, Any

from parser import CharParser, EmptyParser, AndParser, FuncParser, KeyArgument, OrParser
from .common import digit, spaces

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


def generate_operation_2(base_expr, ops: Dict[str, Callable[[Any, Any], Any]]):
    # Создаёт операцию от двух переменных с оператором symbol

    ops_key_parsers = {
        CharParser.line(k): v
        for k, v in ops.items()
    }

    def _func_wrapper(*args, a, op: Union[AndParser], b):
        return ops_key_parsers[op](a, b)

    _func_wrapper.__name__ = f"op_for_{'_'.join(ops.keys())}"

    op_parser = OrParser(*(CharParser.line(k) for k in ops.keys()))

    parser = FuncParser(
        KeyArgument('a', base_expr) & spaces
        & KeyArgument('op', op_parser) & spaces
        & KeyArgument('b', base_expr),
        _func_wrapper
    )

    return parser


number_expressions |= generate_operation_2(number_expressions, {
    "-": operator.sub,
    "+": operator.add
})

number_expressions |= generate_operation_2(number_expressions, {
    "*": operator.mul,
    "/": operator.floordiv
})
