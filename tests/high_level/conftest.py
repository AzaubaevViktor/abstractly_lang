import os
from pprint import pprint

import pytest

from main import live_parser

pprint(dict(os.environ))

from executor import Executor
from source import StrSource


def _executor(raw_line: str):
    executor = Executor(live_parser)

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
