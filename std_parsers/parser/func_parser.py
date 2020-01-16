from line import Line
from parser import FuncParser, KeyArgument, CharParser
from parser.base import BaseParser
from std_parsers.common import spaces, any_str
from std_parsers.variable import variables


def use_func_parser(parser_expr: BaseParser):
    """
    Пока для парсинга функции используется any_str.
    Это медленно, дорого и сложно, но пока это самый простой вариант.

    :param parser_expr:
    :return:
    """

    _p = KeyArgument(
        'parser',
        parser_expr
    ) & spaces & CharParser.line("=>") & spaces \
         & KeyArgument(
        'function_text',
        any_str
    )

    def _f(*result, parser: BaseParser, function_text: str):
        print("FuncParser generator", result, parser, function_text)

        def _generated_function(*_result, _executor=None, **kwargs):
            print("Call generated function:", _result, kwargs)
            print("Append variables")

            variables.update(kwargs)

            return _executor.execute(Line(function_text))

        return FuncParser(
            parser,
            _generated_function
        )

    return FuncParser(
        _p,
        _f
    )
