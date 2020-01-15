from parser import OrParser, CharParser

digit = OrParser(*(CharParser(str(x)) for x in range(10)))

space = CharParser(' ') | CharParser('\t') | CharParser('\n')

spaces = space[:]

