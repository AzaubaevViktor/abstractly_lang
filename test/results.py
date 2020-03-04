from core import AttributeStorage, Attribute
from colorama import Back, Fore


class BaseTestResult(AttributeStorage):
    sorted_id = 100
    NAME = "UNKNOWN"
    SYMBOL = "🚫"
    COLOR = Back.RED + Fore.WHITE

    def __str__(self):
        return "🚫🚫🚫 WRONG TEST RESULT 🚫🚫🚫"


class TestNotRunning(BaseTestResult):
    sorted_id = 0
    NAME = "NOT RUNNING"
    SYMBOL = "💤"
    COLOR = Fore.LIGHTBLACK_EX

    def __str__(self):
        return ""


class TestExecuting(BaseTestResult):
    sorted_id = 10
    NAME = "EXECUTING"
    SYMBOL = "🛠"
    COLOR = Fore.LIGHTBLUE_EX

    def __str__(self):
        return ""


class TestSuccess(BaseTestResult):
    sorted_id = 30
    NAME = "SUCCESS"
    SYMBOL = "✅"
    COLOR = Fore.LIGHTGREEN_EX

    result = Attribute(default=None)

    def __str__(self):
        if self.result:
            return str(self.result)
        return ""


class TestFailed(BaseTestResult):
    sorted_id = 40
    NAME = "FAILED"
    SYMBOL = "⛔️"
    COLOR = Fore.LIGHTRED_EX

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
    COLOR = Fore.YELLOW

    cause: str = Attribute()
    exc_info: 'raises' = Attribute()

    def __str__(self):
        return f"{self.cause} ({self.exc_info.type})"


class TestSkipped(BaseTestResult):
    sorted_id = 20
    NAME = "SKIPPED"
    SYMBOL = "⏩"
    COLOR = Fore.LIGHTWHITE_EX

    cause: str = Attribute()

    def __str__(self):
        return self.cause
