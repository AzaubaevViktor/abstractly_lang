from traceback import print_exc

from line import Line
from parser.base import BaseParser


class Executor:
    def __init__(self, parser: BaseParser):
        self.parser = parser

    def execute(self, line: Line):
        try:
            return self._execute(line)
        except Exception as e:
            print_exc()

    def _execute(self, line: Line):
        results = list(self.parser.parse(line))

        assert len(results) != 0, "Please catch this"

        print("|- Parsed:")
        for result in results:
            print(f"|  - {result}")

        if len(results) > 1:
            print(f"| ⚠️ More than one result")

        result = results[0]

        if result.line:
            print(f"|- Line:")
            print(f"|  `{result.line}`")

        exec_result = result.parser.calculate()

        print(f"|- Execute:")

        print(f"   `{exec_result}`")

        return exec_result
