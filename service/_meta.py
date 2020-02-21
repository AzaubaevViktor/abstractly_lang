import inspect
from typing import Type, List, Dict, Any, Tuple


class HandlerInfo:
    def __init__(self, message_class: "Message" = None):
        self.message_class = message_class or self._generate_message()

    def _generate_message(self):
        class GeneratedMessage:
            def __init__(self, args, kwargs):
                self.args = args
                self.kwargs = kwargs

        return GeneratedMessage


class HandlerAttribute:
    def __init__(self, func, message_class):
        self.func = func
        self.message_class = message_class

    def __get__(self, instance, owner):
        async def _get(*args, **kwargs):
            return await owner.get(self.message_class(*args, **kwargs))
        return _get


class MetaService(type):
    def __new__(cls, name: str, bases: Tuple[Type["Service"]], attrs: Dict[str, Any]):
        new_attrs = {}

        for k, v in attrs.items():
            if hasattr(v, "__handler_info__"):
                handler_info: HandlerInfo = v.__handler_info__
                new_attrs[k] = HandlerAttribute(
                    v, handler_info.message_class
                )
            else:
                new_attrs[k] = v

        return super().__new__(cls, name, bases, new_attrs)


def handler(*args):
    from service import Message

    print(args)

    if isinstance(args[0], type) and issubclass(args[0], Message):
        return handler

    func = args[0]
    assert inspect.iscoroutinefunction(func)
    func.__handler_info__ = HandlerInfo()

    return func
