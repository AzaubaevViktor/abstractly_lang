from line import Line


class ParseVariant:
    def __init__(self, parser: "BaseParser", line: Line):
        self.parser = parser
        self.line = line
        
    def __eq__(self, other: 'ParseVariant'):
        if not isinstance(other, ParseVariant):
            return False

        return (self.parser == other.parser) and (self.line == other.line)

    def __repr__(self):
        return f"<{self.parser}, {self.line}>"
