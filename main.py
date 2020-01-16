from time import time

from executor import Executor
from live_source import LiveSource
from parser import EndLineParser, KeyArgument, FuncParser
from std_parsers import number_expressions, comment_parser
from std_parsers import system_expressions
from std_parsers import parser_parser
from std_parsers.common import spaces
from std_parsers.variable import variables

live_parser = EndLineParser(FuncParser(
    KeyArgument("calc_result", number_expressions | system_expressions | parser_parser)
    & spaces & comment_parser[:2],
    lambda *result, calc_result: calc_result
))

variables['@'] = live_parser
variables['@spaces'] = variables['__'] = spaces

if __name__ == '__main__':
    source = LiveSource()
    executor = Executor(lambda: variables['@'])

    for line in source():
        st = time()
        executor.execute(line)
        tm = time() - st
        print(f"Time: {tm * 1000:.2f}ms")
