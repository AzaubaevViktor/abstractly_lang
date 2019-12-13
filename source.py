from typing import Iterable

from line import Line


class BaseSource:
    def __init__(self, name: str):
        self.name = name

    def __call__(self) -> Iterable["Line"]:
        raise NotImplementedError()

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"


class StrSource(BaseSource):
    def __init__(self, name: str, data: str):
        super().__init__(name)
        self.data = data

    def __call__(self):
        for i, line in enumerate(self.data.split("\n")):
            yield Line(line, i, self)
