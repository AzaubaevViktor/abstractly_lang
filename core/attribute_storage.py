from typing import Optional, Tuple, Type, Any, Dict

from log import Log


class Attribute:
    def __init__(self, description: Optional[str] = None):
        self.description = description


class MetaAttributeStorage(type):
    def __new__(mcs, name: str, bases: Tuple[Type["Service"]], attrs: Dict[str, Any]):
        mcs.logger = Log("MetaAttributeStorage")

        __attributes__ = attrs.get("__attributes__", None)
        if __attributes__:
            raise NotImplementedError("Do not set __attributes__ manually")

        __attributes__ = {}

        for base in bases:
            base: "AttributeStorage"
            if hasattr(base, "__attributes__"):
                __attributes__.update(base.__attributes__)

        for attr_name, attr_value in attrs.items():
            if isinstance(attr_value, Attribute):
                __attributes__[attr_name] = attr_value

        attrs['__attributes__'] = __attributes__

        return super().__new__(mcs, name, bases, attrs)


class AttributeStorage(metaclass=MetaAttributeStorage):
    __attributes__: Dict[str, Attribute]

    def __init__(self, **kwargs):

        for k in self.__attributes__:
            if k not in kwargs:
                raise TypeError(f"Missed argument: {k}")

        for k, v in kwargs.items():
            if k not in self.__attributes__:
                raise TypeError(f"Extra argument: {k}. "
                                f"Try one of: {self.__attributes__.keys()}")
            setattr(self, k, v)
