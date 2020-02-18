from typing import Type, TypeVar

_TM = TypeVar("_TM")


class SearchableSubclasses:
    @classmethod
    def search(cls: _TM, name: str) -> Type[_TM]:
        for klass in cls.__subclasses__():
            klass: Type[_TM]
            if klass.__name__ == name:
                return klass

        raise NameError(f"Not found service with name {name}. "
                        f"Class must be subclass of `Service`",
                        name, tuple(klass.__name__ for klass in cls.__subclasses__()))
