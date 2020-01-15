from typing import Dict

from parser.base import BaseParser
from parser.parser_wrapper import WrapperParser


class KeyArgument(WrapperParser):
    def __init__(self, key: str, parser: BaseParser):
        super().__init__(parser)
        self.key = key

    def _wrap(self, parser: BaseParser):
        return KeyArgument(self.key, parser)

    def __eq__(self, other: BaseParser):
        _result = super().__eq__(other)
        if _result is not None:
            return _result

        if not isinstance(other, self.__class__):
            return False

        return (self.parser == other.parser) and (self.key == other.key)

    def key_args(self) -> Dict[str, BaseParser]:
        return {
            self.key: self.parser
        }

    def __str__(self):
        return f"[{self.key}: {self.parser}]"

    def __hash__(self):
        return hash(self.__class__) * hash(self.key) * hash(self.parser)
