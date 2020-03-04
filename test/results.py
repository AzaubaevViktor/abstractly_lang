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


class TestWrong(BaseTestResult):
    SYMBOL = "⛔️"

    exc = Attribute()
