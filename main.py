from time import time
from typing import Union

from executor import Executor
from live_source import LiveSource
from parser.common.end_line_parser import EndLineParser
from parser.func.func_parser import FuncParser
from parser.func.key_argument import KeyArgument
from parser.logic.and_parser import AndParser
from parser.logic.char_parser import CharParser
from parser.logic.empty_parser import EmptyParser

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
    num_str = "".join(p.ch for p in number.parsers)
    num = int(num_str)

    if sign:
        num = -num

    return num


_number_parser = EndLineParser(FuncParser(
        KeyArgument('sign', CharParser('-')[:2]) & KeyArgument('number', _digit_parser[1:]),
        p_to_num
    ))


def _exit(*args, **kwargs):
    exit(0)


_exit_parser = EndLineParser(FuncParser(
    CharParser('e') & CharParser('x') & CharParser('i') & CharParser('t'),
    _exit
))


live_parser = _number_parser | _exit_parser


if __name__ == '__main__':
    source = LiveSource()
    executor = Executor(live_parser)

    for line in source():
        st = time()
        executor.execute(line)
        tm = time() - st
        print(f"Time: {tm * 1000:.2f}ms")
