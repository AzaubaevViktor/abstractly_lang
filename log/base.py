import datetime
from enum import Enum


class LogLevel(Enum):
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
        self._level: LogLevel = LogLevel.DEBUG

    @property
    def level(self) -> LogLevel:
        return self._level

    @level.setter
    def level(self, level: LogLevel):
        if not isinstance(level, LogLevel):
            raise TypeError(type(level))
        self._level = level

    def _print(self, level: LogLevel, *args, **kwargs):
        if level.value >= self._level.value:
            now = datetime.datetime.now()
            _args = ' '.join(map(str, args)) if args else ''
            _kwargs = ' '.join((f"{k}={v}" for k, v in kwargs.items())) if kwargs else ''
            print(f"[{now.strftime(self.TIME_FORMAT)}] [{level.name:^10}] {_args} {_kwargs}")

    def deep_debug(self, *args, **kwargs):
        self._print(LogLevel.DEEP_DEBUG, *args, **kwargs)

    def debug(self, *args, **kwargs):
        self._print(LogLevel.DEBUG, *args, **kwargs)

    def info(self, *args, **kwargs):
        self._print(LogLevel.INFO, *args, **kwargs)

    def important(self, *args, **kwargs):
        self._print(LogLevel.IMPORTANT, *args, **kwargs)

    def warning(self, *args, **kwargs):
        self._print(LogLevel.WARNING, *args, **kwargs)

    def exception(self, *args, **kwargs):
        self._print(LogLevel.EXCEPTION, *args, **kwargs)

    def error(self, *args, **kwargs):
        self._print(LogLevel.ERROR, *args, **kwargs)
