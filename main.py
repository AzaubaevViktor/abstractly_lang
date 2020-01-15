from time import time

from executor import Executor
from live_source import LiveSource
from parser import EndLineParser
from std_parsers import number_expressions
from std_parsers import system_expressions
from std_parsers import parser_parser

live_parser = EndLineParser(number_expressions | system_expressions | parser_parser)


if __name__ == '__main__':
    source = LiveSource()
    executor = Executor(live_parser)

    for line in source():
        st = time()
        executor.execute(line)
        tm = time() - st
        print(f"Time: {tm * 1000:.2f}ms")
