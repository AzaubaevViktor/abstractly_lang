from typing import Any

import pytest


def exec_ret(line: str) -> Any:
    _var = {'x': None}
    exec(f"_var['x'] = ({line})", {'_var': _var})
    return _var['x']


@pytest.fixture(scope="function")
def a():
    """
    Clean abstractly executor
    """

    return exec_ret
