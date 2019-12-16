from time import time
from typing import Union, List

from executor import Executor
from live_source import LiveSource
from parser.common.end_line_parser import EndLineParser
from parser.common.simple import spaces
from parser.func.func_parser import FuncParser
from parser.func.key_argument import KeyArgument
from parser.logic.and_parser import AndParser
from parser.logic.char_parser import CharParser
from parser.logic.empty_parser import EmptyParser
from parser.logic.or_parser import OrParser

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


_exit_parser = EndLineParser(FuncParser(
    CharParser('e') & CharParser('x') & CharParser('i') & CharParser('t'),
    _exit
))


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
    spaces & KeyArgument('op', CharParser('*') | CharParser('/')) & spaces & KeyArgument('num', _number_parser),
    _get_mul_coef
)


_term = FuncParser(
        spaces & KeyArgument('a', _number_parser) & KeyArgument('operators', _op_mul_div[:]) & spaces,
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

_expr = EndLineParser(
    FuncParser(
        spaces & KeyArgument('a', _term) & KeyArgument('operators', _op_add_diff[:]) & spaces,
        _f_add_diff
    )
)

# Combine

live_parser = _exit_parser | _expr


if __name__ == '__main__':
    source = LiveSource()
    executor = Executor(live_parser)

    for line in source():
        st = time()
        executor.execute(line)
        tm = time() - st
        print(f"Time: {tm * 1000:.2f}ms")
