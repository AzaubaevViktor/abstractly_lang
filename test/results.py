from core import AttributeStorage, Attribute


class BaseTestResult(AttributeStorage):
    sorted_id = 100
    NAME = "UNKNOWN"
    SYMBOL = "🚫"

    def __str__(self):
        return "🚫🚫🚫 WRONG TEST RESULT 🚫🚫🚫"


class TestNotRunning(BaseTestResult):
    sorted_id = 0
    NAME = "NOT RUNNING"
    SYMBOL = "💤"

    def __str__(self):
        return ""


class TestExecuting(BaseTestResult):
    sorted_id = 10
    NAME = "EXECUTING"
    SYMBOL = "🛠"

    def __str__(self):
        return ""


class TestSuccess(BaseTestResult):
    sorted_id = 30
    NAME = "SUCCESS"
    SYMBOL = "✅"

    result = Attribute(default=None)

    def __str__(self):
        if self.result:
            return str(self.result)
        return ""


class TestFailed(BaseTestResult):
    sorted_id = 40
    NAME = "FAILED"
    SYMBOL = "⛔️"

    exc = Attribute()
    cause = Attribute()
    stack = Attribute()

    def __str__(self):
        # stack = '\n'.join(self.stack)
        return f"{self.cause}\n" \
               f"{self.exc}"


class TestXFailed(BaseTestResult):
    sorted_id = 30
    NAME = "XFAILED"
    SYMBOL = "⚠️"

    cause: str = Attribute()
    exc_info: 'raises' = Attribute()

    def __str__(self):
        return f"{self.cause} ({self.exc_info.type})"


class TestSkipped(BaseTestResult):
    sorted_id = 20
    NAME = "SKIPPED"
    SYMBOL = "⏩"

    cause: str = Attribute()

    def __str__(self):
        return self.cause
