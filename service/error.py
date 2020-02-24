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
