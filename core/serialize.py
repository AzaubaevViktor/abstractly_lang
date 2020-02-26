import json
from json import JSONEncoder, JSONDecoder
from typing import Any


class MessageEncoder(JSONEncoder):
    def default(self, o):
        from service import Message
        if isinstance(o, Message):
            return {
                "@class": o.__class__.__name__,
                **dict(o)
            }
        return super().default(o)


def _message_hook(dct):
    if "@class" in dct:
        msg_class_name = dct['@class']
        from service import Message
        MessageClass = Message.search(msg_class_name)
        del dct['@class']
        return MessageClass(**dct)
    return dct


def serialize(obj: Any):
    return json.dumps(obj, cls=MessageEncoder)


def deserialize(data: str):
    return json.loads(data, object_hook=_message_hook)

