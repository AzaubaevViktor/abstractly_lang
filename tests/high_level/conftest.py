import os
from pprint import pprint

import pytest

from std_parsers import number_expressions

pprint(dict(os.environ))

from executor import Executor
from parser import EndLineParser
from source import StrSource


def _executor(raw_line: str):
    executor = Executor(EndLineParser(number_expressions))

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
