import inspect
import weakref
from typing import Type, List, Dict, Any, Tuple, Awaitable, Union, Callable

from log import Log


_HandlerFuncT = Callable[["Message"], Awaitable[Any]]


class HandlerInfo:
    _BaseGeneratedMessage = None

    def __init__(self, func: _HandlerFuncT, *additional_message_classes: "Message"):
        self.func_ref = weakref.ref(func)

        self.message_classes = (
            self._generate_message_class(),
            *additional_message_classes)

    @property
    def generated_class(self):
        return self.message_classes[0]

    @classmethod
    def _init_base_msg_class(cls):
        if cls._BaseGeneratedMessage is None:
            from service import Message

            class BaseGeneratedMessage(Message):
                def __init__(self, args, kwargs):
                    super(BaseGeneratedMessage, self).__init__()
                    self.args = args
                    self._send_kwargs = kwargs

            cls._BaseGeneratedMessage = BaseGeneratedMessage

    def _generate_message_class(self):
        self._init_base_msg_class()

        return type(f"_{self.func_ref().__name__}~GeneratedMessage",
                    (self._BaseGeneratedMessage, ), {})


class MessageSenderAttribute:
    def __init__(self, attr_name: str, func: _HandlerFuncT, handler_info: HandlerInfo):
        self.attr_name = attr_name
        self.func = func
        self.message_classes = handler_info.message_classes
        self.generated_message_class = handler_info.generated_class

    def __get__(self, instance, owner):
        async def _owner_get(*args, **kwargs):
            from service import Service
            if args and isinstance(args[0], Service):
                args = args[1:]
            return await owner.get(self.generated_message_class(args, kwargs))

        _owner_get.__name__ = f"_{self.generated_message_class.__name__}~owner.get"

        Log("MessageSenderAttribute").debug(f"Inject",
                                            method=_owner_get.__name__,
                                            attr_name=self.attr_name
                                            )

        setattr(owner, self.attr_name, _owner_get)

        return _owner_get


class CallContext:
    def __init__(self, message: "Message", handler_info: HandlerInfo):
        self.message = message
        self.handler_info = handler_info

    @property
    def GeneratedMessageClass(self):
        return self.handler_info.generated_class

    def __repr__(self):
        return f"<CallContext: " \
               f"{type(self.message)} " \
               f">"


class WrappedMethod:
    def __init__(self,
                 func: Callable[..., Awaitable[Any]],
                 _self: "Service" = None):
        self.func = func
        self._self = _self

    async def __call__(self, message: "Message"):
        # assert isinstance(message, self.message_class)
        Log("attr").info("Call WrappedMethod",
                         messaage=message,
                         func=self.func,
                         _self=self._self)

        f_args = message.args
        f_kwargs = message.kwargs

        func_spec = inspect.getfullargspec(self.func)

        if "_ctx" in func_spec.args or \
                "_ctx" in func_spec.kwonlyargs:
            f_kwargs['_ctx'] = CallContext(message, self.func.__handler_info__)

        try:
            return await self.func(self._self, *f_args, **f_kwargs)
        except TypeError as te:
            Log("WrappedMethod").warning(error_args=te.args, error=te,
                                         message=message, func=self.func)
            raise

    def __repr__(self):
        self_s = f"{self._self}:" if self._self else ''
        return f"<WrappedMethod for {self_s} {self.func}>"


class HandlersManager:
    # TODO: Inherit from dict
    def __init__(self, d: dict = None):
        self.handlers: Dict[Type["Message"], _HandlerFuncT] = {}
        self.handlers.update(d or {})

    def __get__(self, instance: "Service", owner: Type["Service"]):
        if instance is None:
            return self

        Log("HandlersManager").debug("Injecting")

        instance._handlers = self._generate_handlers_bounded_to_self(instance)

        instance._handlers_manager = self

        return instance._handlers

    def __getitem__(self, item: Type["Message"]) -> _HandlerFuncT:
        return self.handlers[item]

    def __setitem__(self, key: Type["Message"], value: _HandlerFuncT):
        self.handlers[key] = value

    def __add__(self, other: "HandlersManager") -> "HandlersManager":
        return HandlersManager({**self.handlers, **other.handlers})

    def update(self, other: Union[dict, "HandlersManager"]):
        if isinstance(other, dict):
            self.handlers.update(other)
        elif isinstance(other, HandlersManager):
            self.handlers.update(other.handlers)

    def _generate_handlers_bounded_to_self(self, instance):
        return {
            k: self._inject_self(v, instance)
            for k, v in self.handlers.items()
        }

    def _inject_self(self, v, instance):
        if isinstance(v, WrappedMethod):
            assert not v._self
            return WrappedMethod(v.func, instance)
        return v


class MetaService(type):
    def __new__(mcs, name: str, bases: Tuple[Type["Service"]], attrs: Dict[str, Any]):
        mcs.logger = Log("MetaService")
        new_attrs = MetaService._garbage_handlers(bases, attrs)

        return super().__new__(mcs, name, bases, new_attrs)

    @classmethod
    def _garbage_handlers(mcs, bases, attrs):
        # Bases
        handlers = HandlersManager()
        for base in bases:
            base: "Service"
            if hasattr(base, "_handlers"):
                if isinstance(base._handlers, HandlersManager):
                    handlers += base._handlers
                else:
                    mcs.logger.warning(
                        f"{base._handlers} has type"
                        f"{type(base)} instead"
                        f"{HandlersManager.__name__}"
                    )

        handlers += HandlersManager(attrs.get('_handlers', {}))

        # Attributes
        new_attrs = {}
        message_class_used = []
        for k, v in attrs.items():
            if hasattr(v, "__handler_info__"):
                handler_info: HandlerInfo = v.__handler_info__

                new_attrs[k] = MessageSenderAttribute(k, v, handler_info)

                wrapped_method = WrappedMethod(v)
                for message_class in handler_info.message_classes:
                    if message_class in message_class_used:
                        raise TypeError(
                            f"For handler `{k}`: "
                            f"message type `{message_class.__name__}` already used in other handler"
                            f"`{handlers[message_class]}`"
                        )
                    handlers[message_class] = wrapped_method
                    message_class_used.append(message_class)
            else:
                new_attrs[k] = v

        new_attrs['_handlers'] = handlers

        return new_attrs


def handler(*args, message_types=tuple()):
    from service import Message
    from service.message import Shutdown

    if isinstance(args[0], type) and issubclass(args[0], Message):
        for message in args:
            if issubclass(message, Shutdown):
                raise TypeError(f"Use `shutdown()` method instead Shutdown MessageType")

        def _(func):
            return handler(func, message_types=args)

        return _

    func = args[0]
    assert callable(func), f"{func} must be callable"
    assert inspect.iscoroutinefunction(func), f"{func.__name__} must be `async def`"
    func.__handler_info__ = HandlerInfo(func, *message_types)

    return func
