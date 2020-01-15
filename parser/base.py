from typing import Iterable, Dict, Any, Tuple

from line import Line
from parser.parse_variant import ParseVariant


class MetaParser(type):
    __memo__ = {}

    def __new__(mcls, name: str, bases: Tuple["BaseParser"], attributes: Dict[str, Any]):
        if name != "BaseParser":
            for an, a in attributes.items():
                if callable(a):
                    attributes[an] = mcls._catcher(mcls, a)
                    print(name, an, a)
        return super().__new__(mcls, name, bases, attributes)

    def _memo(mcls, f):
        def _(self, line):
            if (self, line) not in mcls.__memo__:
                mcls.__memo__[(self, line)] = f(self, line)
            return mcls.__memo__[(self, line)]

        _.__name__ = f.__name__
        return _

    def _catcher(mcls, f):
        def _(self, *args, **kwargs):
            try:
                return f(self, *args, **kwargs)
            except BaseParserError as e:
                print("OWOWOW", kwargs)
                if 'self' in kwargs:
                    kwargs['WTF:self'] = kwargs["self"]
                    del kwargs['self']

                e.add_context(
                    _function_name=f.__name__,
                    _self=self,
                    args=args,
                    **kwargs
                )
                raise e
            except Exception as ex:
                raise ex

        _.__name__ = f.__name__
        return _


class BaseParser(metaclass=MetaParser):
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

    def __iter__(self) -> Iterable['BaseParser']:
        """ Список парсеров внутри """
        raise NotImplementedError()


class BaseParserError(Exception):
    def __init__(self, msg: str, parser: BaseParser = None):
        self.msg = msg
        self.parser = parser

    def __str__(self):
        return self.msg


class _ParseContext:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __str__(self):
        return "\n".join((
            f"{k}: {repr(v)}"
            for k, v in self.kwargs.items()
        ))


class ParseError(BaseParserError):
    # TODO: Add pretty print
    def __init__(self, msg: str, **kwargs):
        self.msg = msg
        self.contexts = [_ParseContext(**kwargs)]

    def __str__(self):
        return "\n====\n".join(
            (self.msg, ) + tuple(map(str, self.contexts))
        )

    def add_context(self, **kwargs):
        # TODO: Add context
        #       Line (source, position, etc)
        #       Parser nested (intercept ParseError)
        self.contexts.append(_ParseContext(**kwargs))
