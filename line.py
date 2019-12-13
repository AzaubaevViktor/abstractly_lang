from typing import Optional, Union


class Line:
    def __init__(self, line: str,
                 number: int = 0,
                 source: Optional['BaseSource'] = None,
                 pos: int = 0,
                 parent: "Line" = None
                 ):
        self.line = line
        self.number = number
        self.source = source

        # При взятии подстроки
        self.pos = pos
        self.parent = parent

    def __getitem__(self, item):
        if isinstance(item, slice):
            start = item.start or 0
        else:
            start = item

        # TODO: Переписать вычисление number и source через parent
        return Line(
            line=self.line[item],
            number=self.number,
            source=self.source,
            pos=start,
            parent=self
        )

    def __eq__(self, other: Union[str, "Line"]):
        if isinstance(other, Line):
            return self.line == other.line

        return self.line == other
