from core import AttributeStorage, Attribute


class BaseTestResult(AttributeStorage):
    SYMBOL = "🚫"


class TestNotRunning(BaseTestResult):
    SYMBOL = "💤"


class TestExecuting(BaseTestResult):
    SYMBOL = "🛠"


class TestGood(BaseTestResult):
    SYMBOL = "✅"

    result = Attribute(default=None)


class TestFailed(BaseTestResult):
    SYMBOL = "⛔️"

    exc = Attribute()
    cause = Attribute()
    stack = Attribute()


class TestXFailed(BaseTestResult):
    SYMBOL = "⚠️"

    cause: str = Attribute()
    exc_info = Attribute()


class TestSkipped(BaseTestResult):
    SYMBOL = "⏩"

    cause: str = Attribute()
