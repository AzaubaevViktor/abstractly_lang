import json
from json import JSONEncoder
from typing import Optional, Tuple, Type, Any, Dict, Iterable, TypeVar

from log import Log
from .searchable import SearchableSubclasses


class Attribute:
    def __init__(self, description: Optional[str] = None):
        self.name = None
        self.description = description

    def __get__(self, instance: "AttributeStorage", owner: Type["AttributeStorage"]):
        if instance is None:
            return self

        return instance._storage[self.name]

    def __set__(self, instance: "AttributeStorage", value: "Any"):
        instance._storage[self.name] = value


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
                attr_value.name = attr_name

        attrs['__attributes__'] = __attributes__

        return super().__new__(mcs, name, bases, attrs)


class AttributeStorageEncoder(JSONEncoder):
    def default(self, o):
        print(o)
        if isinstance(o, AttributeStorage):
            return {
                "@class": o.__class__.__name__,
                **dict(o)
            }
        return super().default(o)


def _attribute_storage_hook(dct):
    if "@class" in dct:
        msg_class_name = dct['@class']
        AttributeStorageClass = AttributeStorage.search(msg_class_name)
        del dct['@class']
        return AttributeStorageClass(**dct)
    return dct


AS_T = TypeVar("AS_T", "AttributeStorage", "AttributeStorage")


class AttributeStorage(SearchableSubclasses, metaclass=MetaAttributeStorage):
    __attributes__: Dict[str, Attribute]

    def __init__(self, **kwargs):
        self._storage = {}

        for k in self.__attributes__:
            if k not in kwargs:
                raise TypeError(f"Missed argument: {k}")

        for k, v in kwargs.items():
            if k not in self.__attributes__:
                raise TypeError(f"Extra argument: {k}. "
                                f"Try one of: {self.__attributes__.keys()}")
            setattr(self, k, v)

    def __iter__(self) -> Iterable[Tuple[str, Any]]:
        yield from self._storage.items()

    def serialize(self) -> str:
        return json.dumps(self, cls=AttributeStorageEncoder)

    @classmethod
    def deserialize(cls: Type[AS_T], data: str, force=False) -> AS_T:
        obj = json.loads(data, object_hook=_attribute_storage_hook)
        if (type(obj) is not cls) and not force:
            raise TypeError(f"Deserialized object must be {cls.__name__} type "
                            f"instead {type(obj).__name__}")
        return obj

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return self._storage == other._storage
