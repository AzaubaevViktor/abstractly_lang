import pytest

from executor import Executor
from source import StrSource
from main import _expr


def _executor(raw_line: str):
    executor = Executor(_expr)

    source = StrSource("<test>", raw_line)
    result = None
    for line in source():
        result = executor.execute(line)
    return result


@pytest.fixture(scope="function")
def a():
    """
    Clean abstractly executor
    """

    return _executor
