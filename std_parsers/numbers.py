from typing import Union

from parser import CharParser, EmptyParser, AndParser, FuncParser, KeyArgument, OrParser
from .common import digit


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

