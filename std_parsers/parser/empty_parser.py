from parser import FuncParser, CharParser, EmptyParser

empty_parser = FuncParser(
    CharParser('∅'),
    lambda *result: EmptyParser()
)
