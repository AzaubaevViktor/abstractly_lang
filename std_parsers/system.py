from parser import FuncParser, CharParser, OrParser

system_expressions = OrParser()

exit_parser = FuncParser(
    CharParser.line("exit"),
    exit
)

system_expressions |= exit_parser
