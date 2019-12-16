from parser.logic.char_parser import CharParser

space_parser = CharParser(' ') | CharParser('\t') | CharParser('\n')

spaces = space_parser[:]
