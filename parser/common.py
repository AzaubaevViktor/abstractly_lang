from parser.logic.char_parser import CharParser

space_parser = CharParser(' ') | CharParser('\t') | CharParser('\n')

# spaces_parser = space[0:]  # RepeatParser(space, 0, None)
