from typing import Type, List, Dict, Any, Tuple


class MetaService(type):
    def __new__(cls, name: str, bases: Tuple[Type["Service"]], attrs: Dict[str, Any]):
        return super().__new__(cls, name, bases, attrs)


def handler(*args):
    from service import Message

    print(args)

    if isinstance(args[0], type) and issubclass(args[0], Message):
        return handler

    def _(*args, **kwargs):
        raise NotImplementedError()

    return _
