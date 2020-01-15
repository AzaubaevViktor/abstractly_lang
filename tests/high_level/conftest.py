import os
from pprint import pprint

import pytest

pprint(dict(os.environ))

from executor import Executor
from parser import EndLineParser
from source import StrSource
from main_v0 import _expr


def _executor(raw_line: str):
    executor = Executor(EndLineParser(_expr))

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
