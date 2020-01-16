from typing import Union, List

from parser import OrParser, CharParser, FuncParser, KeyArgument

digit = OrParser(*(CharParser(str(x)) for x in range(10)))

space = CharParser(' ') | CharParser('\t') | CharParser('\n')

spaces = space[:]

correct_var_symbol = "@:qwertyuiopasdfghjklzxcvbnm"


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


def raw_text(chars: str):
    assert isinstance(chars, str)

    def _to_str(self, _key: Union[CharParser, List[CharParser]]):
        if isinstance(_key, list):
            _key = "".join(p.ch for p in _key)
        else:
            _key = _key.ch
        return _key

    correct_char = OrParser(*(CharParser(x) for x in chars))

    return FuncParser(
        KeyArgument('_key', correct_char[1:]),
        _to_str
    )


var_name = raw_text(correct_var_symbol)
