from time import time

from _help import abs_help
from executor import Executor
from live_source import LiveSource
from parser import EndLineParser, KeyArgument, FuncParser
from std_parsers import number_expressions, comment_parser
from std_parsers import system_expressions
from std_parsers import parser_parser
from std_parsers.common import spaces
from std_parsers.variable import variables

_core_parser = number_expressions | system_expressions | parser_parser

live_parser = EndLineParser(FuncParser(
    KeyArgument("calc_result", _core_parser)
    & spaces & comment_parser[:2],
    lambda *result, calc_result: calc_result
))

variables['@@'] = live_parser
variables['@'] = _core_parser
variables['@spaces'] = variables['__'] = spaces
variables['help'] = abs_help

if __name__ == '__main__':
    source = LiveSource()
    executor = Executor(lambda: variables['@@'])

    variables['_debug'] = executor.change_debug

    print("Hello from Abstractly[iter0]!")
    print("Here is prototype.")
    print("For any help you can go:")
    print("* Online help:  https://github.com/KorovinViktor/abstractly_lang/blob/master/Readme.md")
    print("* Just type help()")

    for line in source():
        st = time()
        executor.execute(line)
        tm = time() - st
        print(f"Time: {tm * 1000:.2f}ms")
