from parser.logic.char_parser import CharParser

_space = CharParser(' ') | CharParser('\t') | CharParser('\n')

# spaces_parser = space[0:]  # RepeatParser(space, 0, None)
