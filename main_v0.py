import math
from time import time
from typing import Union, List

from executor import Executor
from live_source import LiveSource
from parser import AndParser, OrParser, RepeatParser
from parser import CharParser
from parser import EndLineParser
from parser import FuncParser
from parser import KeyArgument
from parser import EmptyParser
from parser.base import BaseParser
from std_parsers.common import spaces

_digit_parser = CharParser('0') \
                | CharParser('1') \
                | CharParser('2') \
                | CharParser('3') \
                | CharParser('4') \
                | CharParser('5') \
                | CharParser('6') \
                | CharParser('7') \
                | CharParser('8') \
                | CharParser('9')


def p_to_num(result, sign: Union[CharParser, EmptyParser], number: AndParser):
    print(result, sign, number)
    num_str = "".join(p.ch for p in number)
    num = int(num_str)

    if sign:
        num = -num

    return num


_number_parser = FuncParser(
        KeyArgument('sign', CharParser('-')[:2]) & KeyArgument('number', _digit_parser[1:]),
        p_to_num
    )


def _exit(*args, **kwargs):
    exit(0)


_exit_parser = FuncParser(
    CharParser('e') & CharParser('x') & CharParser('i') & CharParser('t'),
    _exit
)

# Number factorial


def _f_fact(parser, result: int):
    return math.factorial(result)


_factorial = FuncParser(
    KeyArgument("result", _number_parser) & CharParser('!'),
    _f_fact
)

_number_parser_ng = _number_parser | _factorial

# Calculator


def _f_mul_div(parser, a: int, operators: Union[EmptyParser, List[float]]):
    if not operators:
        operators = []
    operators.append(a)
    result = 1
    for coef in operators:
        result *= coef
    return result


def _get_mul_coef(*args, op: CharParser, num: int):
    if op == CharParser("*"):
        return num
    if op == CharParser("/"):
        return 1 / num
    raise NotImplementedError(f"Don't know what to do with {repr(op)}")


_op_mul_div = FuncParser(
    spaces & KeyArgument('op', CharParser('*') | CharParser('/')) & spaces & KeyArgument('num', _number_parser_ng),
    _get_mul_coef
)


_term = FuncParser(
        spaces & KeyArgument('a', _number_parser_ng) & KeyArgument('operators', _op_mul_div[:]) & spaces,
        _f_mul_div
    )


# =======

def _f_add_diff(parser, a: int, operators: Union[EmptyParser, List[float]]):
    if not operators:
        operators = []
    operators.append(a)
    return sum(operators)


def _get_add_coef(*args, op: CharParser, num: int):
    if op == CharParser("+"):
        return num
    if op == CharParser("-"):
        return - num
    raise NotImplementedError(f"Don't know what to do with {repr(op)}")


_op_add_diff = FuncParser(
    spaces & KeyArgument('op', CharParser('+') | CharParser('-')) & spaces & KeyArgument('num', _term),
    _get_add_coef
)

# Comment
_symbols = " \t\nqwertyuiop[]asdfghjkl;'\\zxcvbnm,./QWERTYUIOP{}ASDFGHJKL:\"|ZXCVBNM<>?" \
           "1234567890-=" \
           "!@#$%^&*()_+" \
           "№%:,.;()_+"
_any_symbol = OrParser(*(CharParser(ch) for ch in _symbols))

_comment = CharParser("#") & _any_symbol[:]


# Parser generator parser

def _char_generator_func(*args, ch: CharParser):
    return ch


_char_generator = FuncParser(
    CharParser("'") & KeyArgument('ch', _any_symbol) & CharParser("'"),
    _char_generator_func
)

_parser_parser = OrParser(_char_generator)


def _or_generator_func(*args, a: BaseParser, b: BaseParser):
    return OrParser(a, b)


_or_parser_generator = FuncParser(
    KeyArgument('a', _parser_parser) & spaces & CharParser('|') & spaces & KeyArgument('b', _parser_parser),
    _or_generator_func
)

_parser_parser |= _or_parser_generator


# Почему это работает?
def _and_generator_func(*args, a: BaseParser, b: BaseParser):
    return AndParser(a, b)


_and_parser_generator = FuncParser(
    KeyArgument('a', _parser_parser) & spaces & CharParser('&') & spaces & KeyArgument('b', _parser_parser),
    _and_generator_func
)

_parser_parser |= _and_parser_generator


# Expression


_expr = FuncParser(
        spaces & KeyArgument('a', _term) & KeyArgument('operators', _op_add_diff[:]) & spaces,
        _f_add_diff
    )

# Repeat

def _repeat_generator_func(*args, a: BaseParser, _from: int, _to: int):
    return a[_from:_to]


_repeat_parser_generator = FuncParser(
    KeyArgument('a', _parser_parser)
        & CharParser('[') & KeyArgument('_from', _expr) & CharParser(':') & KeyArgument('_to', _expr) & CharParser(']')
    ,
    _repeat_generator_func
)

_parser_parser |= _repeat_parser_generator


live_parser = EndLineParser((_exit_parser | _expr | _parser_parser))


if __name__ == '__main__':
    source = LiveSource()
    executor = Executor(live_parser)

    for line in source():
        st = time()
        executor.execute(line)
        tm = time() - st
        print(f"Time: {tm * 1000:.2f}ms")
