from parser.logic.char_parser import CharParser

space_parser = CharParser(' ') | CharParser('\t') | CharParser('\n')

spaces = space_parser[:]

digit_parser =    CharParser('0') \
                | CharParser('1') \
                | CharParser('2') \
                | CharParser('3') \
                | CharParser('4') \
                | CharParser('5') \
                | CharParser('6') \
                | CharParser('7') \
                | CharParser('8') \
                | CharParser('9')
                