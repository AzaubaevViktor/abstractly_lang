from typing import Iterable

from line import Line
from parser.base import BaseParser
from parser.parse_variant import ParseVariant
from parser.parser_wrapper import WrapperParser


class BasePriority:
    def __init__(self, priority: int):
        self.priority = priority

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.priority == other.priority


class PriorityParser(WrapperParser):
    """
    Использует парсер и экземпляр отнаследованного класса BasePriority
    Если в результате парсинга получилось так, что внутри данного парсера
    есть парсер с меньшим/большим приоритетом, то он этот вариант пропускает.
    """

    def __hash__(self):
        return hash(self.__class__) * hash(self.priority) * hash(self.parser)

    def __init__(self, parser: BaseParser, priority: BasePriority):
        if not isinstance(priority, BasePriority):
            raise TypeError(f"Use BasePriority instance instead {type(priority)}")
        super().__init__(parser)
        self.priority = priority

    def _wrap(self, parser: BaseParser):
        return PriorityParser(parser, self.priority)

    def parse(self, line: Line) -> Iterable[ParseVariant]:
        for variant in self.parser.parse(line):
            is_good = True
            for sub in variant.parser:
                if isinstance(sub, PriorityParser):
                    if sub.priority.priority < self.priority.priority:
                        is_good = False
                        break
            if is_good:
                yield ParseVariant(
                    self._wrap(variant.parser),
                    variant.line
                )

    def __eq__(self, other):
        _result = super().__eq__(other)
        if _result is not None:
            return _result

        if isinstance(other, self.__class__):
            return self.parser == other.parser and self.priority == other.priority

        return False

    # def __repr__(self):
    #     return f"<PriorityParser({self.priority}) {self.parser}>"
