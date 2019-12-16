from typing import Iterable

from line import Line
from source import BaseSource


class LiveSource(BaseSource):
    def __init__(self):
        super().__init__("<input>")
        self.line_n = 0

    def __call__(self) -> Iterable["Line"]:
        while True:
            self.line_n += 1
            yield Line(
                input(".=> "),
                self.line_n,
                self
            )
