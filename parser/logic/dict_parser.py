from typing import Iterable, Union, List

from line import Line
from parser import FuncParser, OrParser, CharParser, KeyArgument
from parser.base import BaseParser
from parser.parse_variant import ParseVariant


class DictParser(BaseParser):
    """
    Парсит всё из словаря
    """
    def __init__(self, d, _return_keys=False, **kwargs,):
        self.d = {} if d is None else d

        self.d.update(**kwargs)
        self._return_keys = _return_keys

    def _calc(self, *result, key: Union[CharParser, List[CharParser]]):
        key = self._calc_key(key)

        return self.d[key]

    def _calc_key(self, key):
        if isinstance(key, list):
            key = "".join(p.ch for p in key)
        else:
            key = key.ch
        return key

    def _generate_parser(self) -> BaseParser:
        """ Пока генерируем постоянно """
        if self._return_keys:
            f = self._calc_key
        else:
            f = self._calc

        words = OrParser(*(CharParser.line(key) for key in self.d.keys()))
        return FuncParser(
            KeyArgument('key', words),
            f
        )

    def parse(self, line: Line) -> Iterable[ParseVariant]:
        for variant in self._generate_parser().parse(line):
            yield variant

    def __hash__(self):
        raise NotImplementedError("Not need for this")

    def __iter__(self) -> Iterable['BaseParser']:
        pass
