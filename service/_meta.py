import inspect
from typing import Type, List, Dict, Any, Tuple

from log import Log


class HandlerInfo:
    def __init__(self, message_class: "Message" = None):
        self.message_class = message_class or self._generate_message()

    def _generate_message(self):
        from service import Message

        class GeneratedMessage(Message):
            def __init__(self, args, kwargs):
                super(GeneratedMessage, self).__init__()
                self.args = args
                self.kwargs = kwargs

        return GeneratedMessage


class MessageSenderAttribute:
    def __init__(self, func, message_class):
        self.func = func
        self.message_class = message_class

    def __get__(self, instance, owner):
        async def _get(*args, **kwargs):
            return await owner.get(self.message_class(args, kwargs))
        return _get


class WrappedMethod:
    def __init__(self, func, _self=None):
        self.func = func
        self._self = _self

    async def __call__(self, message: "Message"):
        # assert isinstance(message, self.message_class)
        Log("attr").info("!!!!!", message)
        return await self.func(self._self, *message.args, **message.kwargs)


class HandlersOperator:
    def __init__(self, d: dict):
        self.handlers = {}
        self.handlers.update(d)

    def __get__(self, instance, owner):
        if instance is None:
            raise NotImplementedError()

        instance._handlers = self._generate_dict(instance)

        return instance._handlers

    def _generate_dict(self, instance):
        return {
            k: self._process_method(v, instance)
            for k, v in self.handlers.items()
        }

    def _process_method(self, v, instance):
        if isinstance(v, WrappedMethod):
            assert not v._self
            return WrappedMethod(v.func, instance)
        return v


class MetaService(type):
    def __new__(cls, name: str, bases: Tuple[Type["Service"]], attrs: Dict[str, Any]):
        # TODO: Inheritance
        handlers = attrs.get('_handlers', {})

        new_attrs = {}

        for k, v in attrs.items():
            if hasattr(v, "__handler_info__"):
                handler_info: HandlerInfo = v.__handler_info__
                new_attr = MessageSenderAttribute(v, handler_info.message_class)
                new_attrs[k] = new_attr
                handlers[handler_info.message_class] = WrappedMethod(v)
            else:
                new_attrs[k] = v

        new_attrs['_handlers'] = HandlersOperator(handlers)

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
