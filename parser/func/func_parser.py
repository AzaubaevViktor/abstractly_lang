import inspect
from typing import Callable, Any

from parser.base import BaseParser
from parser.parser_wrapper import WrapperParser


class FuncParser(WrapperParser):
    def __init__(self, parser: BaseParser, func: Callable):
        super().__init__(parser)
        self.func = func

    def _wrap(self, parser: BaseParser):
        return FuncParser(parser, self.func)

    def calculate(self, executor: 'Executor') -> Any:
        kwargs = {k: p.calculate(executor) for k, p in self.parser.key_args().items()}

        if "_executor" in inspect.signature(self.func).parameters:
            kwargs['_executor'] = executor

        return self.func(
            self.parser,
            **kwargs
        )

    def __eq__(self, other: BaseParser):
        _result = super().__eq__(other)
        if _result is not None:
            return _result

        if not isinstance(other, self.__class__):
            return False

        return (self.parser == other.parser) and (self.func == other.func)

    def __str__(self):
        return f"{{{self.parser}}} => {self.func}"

    def __hash__(self):
        return hash(self.__class__) * hash(self.func) * hash(self.parser)
