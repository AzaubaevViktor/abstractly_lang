from parser import CharParser, FuncParser, DictParser, BasePriority, KeyArgument, PriorityParser

from .base import parser_parser


class PriorityDictParser(DictParser):
    def __init__(self):
        self._return_keys = False

    @property
    def d(self):
        return {klass.__name__: klass for klass in BasePriority.__subclasses__()}

def use_priority_parser(number_parser):
    _p = KeyArgument('parser', parser_parser) & \
         CharParser('[') & \
         KeyArgument('priority_class', PriorityDictParser()) & \
         CharParser.line('][') & \
         KeyArgument('priority_value', number_parser) & \
         CharParser(']')

    def _f(result, parser, priority_class, priority_value):
        print(parser, priority_class, priority_value)

        return PriorityParser(parser, priority_class(priority_value))

    priority_parser = FuncParser(
        _p,
        _f
    )

    return priority_parser
