import math

import pytest

from tests.high_level._exec_ret import exec_ret


def test_simple(a):
    assert a("1") == 1


@pytest.mark.parametrize("expr", (
    "1",
    "20",
    "-10",
    "123456789",
    "-12931293128",
    "0"))
def test_simple_op(a, expr):
    assert a(expr) == exec_ret(expr)
    