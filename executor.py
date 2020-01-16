from traceback import print_exc
from typing import Union, Callable

from line import Line
from parser.base import BaseParser


class Executor:
    def __init__(self, parser: Union[BaseParser, Callable]):
        self._parser = parser

    @property
    def parser(self):
        if callable(self._parser):
            return self._parser()
        return self._parser

    def execute(self, line: Line):
        try:
            return self._execute(line)
        except Exception as e:
            print_exc()

    def _execute(self, line: Line):
        results = list(self.parser.parse(line))

        assert len(results) != 0, "Please catch this"

        if len(results) > 1:
            print(f"| ⚠️ More than one result")

        for result in results:
            print("|- Parsed:")
            print(f"|  - {result}")

            if result.line:
                print(f"|- Line:")
                print(f"|  `{result.line}`")

            print(f"|- Execute:")
            print(f"|")

            exec_result = result.parser.calculate(self)

            print(f"|- Finished. Result:")
            print(f"   `{exec_result}`")

        return exec_result
