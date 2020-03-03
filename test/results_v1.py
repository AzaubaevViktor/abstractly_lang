class TestResult:
    result_id = "UNKNOWN"
    sort_id = 0
    sign = "∅"

    def __str__(self):
        raise NotImplementedError()


class TestInProgress(TestResult):
    result_id = "IN_PROGRESS"
    sort_id = 1
    sign = "❓"

    def __str__(self):
        return ""


class TestGood(TestResult):
    result_id = "GOOD"
    sort_id = 3
    sign = "✅"

    def __init__(self, result):
        self.result = result

    def __str__(self):
        return "" if self.result is None else str(self.result)


class TestFailed(TestResult):
    result_id = "FAILED"
    sort_id = 100
    sign = "⛔️"

    def __init__(self, exc, msg):
        self.exc = exc
        self.msg = msg

    def __str__(self):
        return f"{self.exc}:\n {self.msg}"


class TestSkipped(TestResult):
    result_id = "SKIPPED"
    sort_id = 2
    sign = "⏩"

    def __init__(self, cause):
        self.cause = cause

    def __str__(self):
        return str(self.cause)


class TestMustFailed(TestResult):
    result_id = "MUST FAILED"
    sort_id = 4
    sign = "⚠️"

    def __init__(self, cause, exc_info):
        self.cause = cause
        self.exc_info = exc_info

    def __str__(self):
        return f"{self.cause}: {self.exc_info}"