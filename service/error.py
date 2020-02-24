from typing import Type, Dict


class BaseServiceError(Exception):
    pass


class UnknownMessageType(BaseServiceError):
    def __init__(self, service: "Service", message: "Message"):
        self.service = service
        self.message = message

    def __str__(self):
        return f"Service {self.service.__class__.__name__} " \
               f"cannot process {self.message.__class__.__name__}. " \
               f"Try:\n" \
               f"- Check message name\n" \
               f"- Use hadler\n" \
               f"- Add handler\n" \
               f"- Add message processing into `process` method"


class MetaServiceError(BaseServiceError):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class HandlerMessageBooked(MetaServiceError):
    def __init__(self,
                 handler_name: str,
                 message_class: Type["Message"],
                 handlers: "HandlersManager"):
        self.handler_name = handler_name
        self.message_class = message_class
        self.handlers = handlers

    def __str__(self):
        return f"For handler `{self.handler_name}`: " \
               f"message type `{self.message_class.__name__}` already used in other handler" \
               f"`{self.handlers[self.message_class]}`"


class WrongHandlerMessageType(MetaServiceError):
    def __init__(self, message_class: Type["Message"], msg: str):
        self.message_class = message_class
        super().__init__(msg)

    def __str__(self):
        return f"Wrong message type: {self.message_class.__name__}; {self.msg}"


class WrongHandlerFunc(MetaServiceError):
    pass


class ServiceExist(BaseServiceError):
    def __init__(self, service_instance):
        self.instance = service_instance

    def __str__(self):
        return f"⚠️ 🔥 SYSTEM ERROR 🔥 ⚠️: " \
               f"Instance of Service {self.instance.__class__.__name__} already exist"

