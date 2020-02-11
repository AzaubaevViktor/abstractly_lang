import datetime
from enum import Enum


class _LogLevel(Enum):
    DEEP_DEBUG = -100
    DEBUG = 0
    INFO = 100
    IMPORTANT = 200
    WARNING = 300
    EXCEPTION = 400
    ERROR = 1000


class Log:
    TIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

    def __init__(self, name: str):
        self.name = name
        self.level = _LogLevel.DEBUG

    def _print(self, level: _LogLevel, *args, **kwargs):
        if level.value >= self.level.value:
            now = datetime.datetime.now()
            _args = ' '.join(map(str, args)) if args else ''
            _kwargs = ' '.join((f"{k}={v}" for k, v in kwargs.items())) if kwargs else ''
            print(f"[{now.strftime(self.TIME_FORMAT)}] [{level.name:^10}] {_args} {_kwargs}")

    def deep_debug(self, *args, **kwargs):
        self._print(_LogLevel.DEEP_DEBUG, *args, **kwargs)

    def debug(self, *args, **kwargs):
        self._print(_LogLevel.DEBUG, *args, **kwargs)

    def info(self, *args, **kwargs):
        self._print(_LogLevel.INFO, *args, **kwargs)

    def important(self, *args, **kwargs):
        self._print(_LogLevel.IMPORTANT, *args, **kwargs)

    def warning(self, *args, **kwargs):
        self._print(_LogLevel.WARNING, *args, **kwargs)

    def exception(self, *args, **kwargs):
        self._print(_LogLevel.EXCEPTION, *args, **kwargs)

    def error(self, *args, **kwargs):
        self._print(_LogLevel.ERROR, *args, **kwargs)
