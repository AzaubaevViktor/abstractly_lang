import pytest

from tests.high_level._exec_ret import exec_ret


@pytest.fixture(scope="function")
def a():
    """
    Clean abstractly executor
    """

    return exec_ret
