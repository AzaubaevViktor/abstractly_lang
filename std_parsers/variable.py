import math
from typing import Any

from parser import DictParser, CharParser, FuncParser, KeyArgument
from parser.base import BaseParser
from std_parsers.common import spaces, symbol

variables = {
    'hello': 'world!',
    'pi': math.pi,
}


def use_variables(key: str, base_parser: BaseParser) -> BaseParser:
    get_var_parser = DictParser(variables)

    def _set_var_func(*result, name, value: Any):
        if isinstance(name, list):
            name = "".join(x.ch for x in name)
        else:
            name = name.ch

        get_var_parser.d[name] = value

        return value

    set_var_parser = FuncParser(
        KeyArgument('name', symbol[1:]) & spaces & CharParser('=') & spaces & KeyArgument('value', base_parser),
        _set_var_func)

    get_var_parser.d[key] = base_parser

    return get_var_parser | set_var_parser
