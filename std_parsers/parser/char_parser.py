from parser import FuncParser, CharParser, DictParser, KeyArgument, EmptyParser
from std_parsers.variable import variables

chars_dict = {
    '\\\\': '\\',
    '\\"': '"',
    "\\'": "'",
    "\\t": "\t",
    **{x: x for x in "1234567890-=qwertyuiop[]asdfghjkl;'zxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM,./!@#$%^&*()_+"}
}

chars_dict_parser = DictParser(chars_dict)

variables['@:chars_dict'] = chars_dict

_p = CharParser('`') & KeyArgument('chars', chars_dict_parser[:]) & CharParser('`')


def _f(*result, chars):
    if isinstance(chars, list):
        chars = "".join(x for x in chars)
    elif isinstance(chars, CharParser):
        chars = chars.s
    elif isinstance(chars, EmptyParser):
        chars = ""
    else:
        raise ValueError(chars)

    return CharParser.line(chars)


char_parser = FuncParser(
    _p,
    _f
)
