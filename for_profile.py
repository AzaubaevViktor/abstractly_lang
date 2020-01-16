from time import time

from executor import Executor
from parser import EndLineParser, KeyArgument, FuncParser
from source import StrSource
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

executor = Executor(lambda: variables['@@'])

lines = """__p = a:@number & __ & `^_^` & __ & b:@number
__fp = __p => @power(a, b)
@ |= __fp
2 ^_^ 3
"""

source = StrSource("profile", lines)

for line in source():
    print("Start parse: ", line)
    st = time()
    executor.execute(line)
    tm = time() - st
    print(f"Time: {tm * 1000:.2f}ms")
