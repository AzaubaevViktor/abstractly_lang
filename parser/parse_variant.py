from line import Line


class ParseVariant:
    def __init__(self, parser: "BaseParser", line: Line):
        self.parser = parser
        self.line = line

    def __repr__(self):
        return f"<{self.parser}, {self.line}>"