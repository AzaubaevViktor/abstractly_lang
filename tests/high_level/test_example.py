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
    "0",
    # TODO: Divide here
    "1 + 2",
    "5 / 2",
    "5 - 2",
    "2 * 3 + 4",
    "1 + 2 - 3",
    "11 + 22 - 33",
    "4 + 2 * 3",
    "4 - 2 * 3",
    "2 + 3 * 4 - 5",
))
def test_simple_op(a, expr):
    assert a(expr) == exec_ret(expr)


@pytest.mark.parametrize("value", tuple(range(0, 10)))
def test_factorial(a, value):
    expr = f"{value}!"
    assert a(expr) == math.factorial(value)
