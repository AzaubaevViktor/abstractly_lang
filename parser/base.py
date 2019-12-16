from typing import Iterable, Dict, Any

from line import Line
from parser.parse_variant import ParseVariant


class BaseParser:
    def parse(self, line: Line) -> Iterable[ParseVariant]:
        """
        Возвращать (парсеры и строки) нужно через yield
        Парсер и строку нужно создавать НОВУЮ
        """
        raise NotImplementedError()

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    def __eq__(self, other):
        if not isinstance(other, BaseParser):
            return False

        if not isinstance(other, self.__class__):
            return False

        if self is other:
            return True

    def __getitem__(self, item):
        from parser.logic.repeat_parser import RepeatParser

        if isinstance(item, slice):
            if item.step is not None:
                raise ValueError(f"Do not use `steps`: ({item.step})")
            return RepeatParser(self, item.start, item.stop)
        else:
            raise NotImplementedError("Slice only")

    def __or__(self, other: 'BaseParser'):
        from parser.logic.or_parser import OrParser
        return OrParser(self, other)

    def __and__(self, other: 'BaseParser'):
        from parser.logic.and_parser import AndParser
        return AndParser(self, other)

    def __hash__(self):
        raise NotImplementedError()

    def key_args(self) -> Dict[str, 'BaseParser']:
        return {}

    def calculate(self) -> Any:
        return self

    def _search(self, parser: 'BaseParser'):
        if self is parser:
            return True

        from parser.logic._multi_parser import MultiParser
        if isinstance(parser, MultiParser):
            return any(map(self._search, parser.parsers))

        return False


class BaseParserError(Exception):
    def __init__(self, msg: str, parser: BaseParser = None):
        self.msg = msg
        self.parser = parser

    def __str__(self):
        return self.msg


class ParseError(BaseParserError):
    # TODO: Add pretty print
    def __init__(self, msg: str):
        self.msg = msg

    def __str__(self):
        return self.msg

    def add_context(self):
        # TODO: Add context
        #       Line (source, position, etc)
        #       Parser nested (intercept ParseError)
        raise NotImplementedError()
