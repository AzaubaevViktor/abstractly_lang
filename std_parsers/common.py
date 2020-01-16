from parser import OrParser, CharParser

digit = OrParser(*(CharParser(str(x)) for x in range(10)))

space = CharParser(' ') | CharParser('\t') | CharParser('\n')

spaces = space[:]

var_symbol = OrParser(*(CharParser(x) for x in "@:qwertyuiopasdfghjklzxcvbnm"))

_all_symbols = "1234567890-=" \
               "qwertyuiop[]" \
               "asdfghjkl;\'\"\\" \
               "zxcvbnm,./" \
               "!@#$%^&*()_+" \
               "QWERTYUIOP{}" \
               "ASDFGHJKL:|" \
               "ZXCVBNM<>?" \
               "~`><" \
               " \t" \
               "№" \
               "йцукенгшщзхъЙЦУКЕНГШЩЗХЪ" \
               "фывапролджэёФЫВАПРОЛДЖЭЁ" \
               "ячсмитьбюЯЧСМИТЬБЮ"
all_symbol = OrParser(*(CharParser(x) for x in _all_symbols))
