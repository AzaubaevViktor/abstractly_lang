import math
from typing import Any

from parser import DictParser, CharParser, FuncParser, KeyArgument
from parser.base import BaseParser
from std_parsers.common import spaces, var_name

variables = {
    'hello': 'world!',
    'pi': math.pi,
}


def use_variables(key: str, base_parser: BaseParser) -> BaseParser:
    get_var_parser = DictParser(variables)

    def _set_var_func(*result, name: str, value: Any):
        get_var_parser.d[name] = value

        return value

    set_var_parser = FuncParser(
        KeyArgument('name', var_name) & spaces & CharParser('=') & spaces & KeyArgument('value', base_parser),
        _set_var_func)

    get_var_parser.d[key] = base_parser

    return get_var_parser | set_var_parser
