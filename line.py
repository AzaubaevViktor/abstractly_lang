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

    def __getitem__(self, item) -> "Line":
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

    def __len__(self):
        return len(self.line)

    @property
    def empty(self) -> bool:
        return not bool(self.line)

    def __repr__(self):
        _parent = '^' if self.parent else ''
        _source = f"{self.source}:" if self.source else ''
        _pos = f"{{{self.pos}}}:" if self.pos else ''
        return f"<Line{_parent}:" \
               f"{_source}" \
               f"{self.number}:" \
               f"{_pos} " \
               f"{repr(self.line)}>"

    def __str__(self):
        return self.line

    def __bool__(self):
        return bool(self.line)

    def __hash__(self):
        return hash(self.line)
