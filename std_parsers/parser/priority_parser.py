from parser import CharParser, FuncParser, DictParser, BasePriority, KeyArgument, PriorityParser
from ..common import spaces


class PriorityDictParser(DictParser):
    def __init__(self):
        self._return_keys = False

    @property
    def d(self):
        return {klass.__name__: klass for klass in BasePriority.__subclasses__()}


def use_priority_parser(number_parser, base_parser):
    _p = CharParser('[') & spaces & \
         KeyArgument('parser', base_parser) & spaces & \
         CharParser("/") & spaces & \
         KeyArgument('priority_class', PriorityDictParser()) & spaces & \
         CharParser("/") & spaces & \
         KeyArgument('priority_value', number_parser) & spaces & \
         CharParser(']')


    def _f(result, parser, priority_class, priority_value):
        print(parser, priority_class, priority_value)

        return PriorityParser(parser, priority_class(priority_value))

    priority_parser = FuncParser(
        _p,
        _f
    )

    return priority_parser
