import math
from itertools import product

import pytest

from tests.high_level._exec_ret import exec_ret


@pytest.mark.parametrize("expr", (
    "1 + 2",
    "5 / 2",
    "5 - 2",
    "2 * 3 + 4",
    "1 + 2 - 3",
    "11 + 22 - 33",
    "4 + 2 * 3",
    "4 - 2 * 3",
    "2 + 3 * 4 - 5",
    "1 + 2 * 3 - 1 + 3 * 4"
))
def test_simple_op(a, expr):
    assert a(expr) == exec_ret(expr)


@pytest.mark.parametrize("value", tuple(range(0, 10)))
def test_factorial(a, value):
    expr = f"{value}!"
    assert a(expr) == math.factorial(value)


@pytest.mark.parametrize("x, y", (
    *product(
        range(0, 10),
        range(0, 10)
    ),
))
def test_factorial_sum(a, x, y):
    result = math.factorial(x) + math.factorial(y)

    assert a(f"{x}! + {y}!") == result

@pytest.mark.parametrize("x, y", (
    *product(
        range(0, 10),
        range(0, 10)
    ),
))
def test_power(a, x, y):
    assert a(f"{x} ** {y}") == math.pow(x, y)

@pytest.mark.parametrize("expr, expected", [
    ("5! / 4!", 5),
    ("2! ** 3! + 1", 65),
    ("2 ** 2 / 2", 2),
    ("2 ** (2 / 2)", 2),
    ("-2 ** 3", -8),
    ("-2 ** 2", 4),
    ("2 ** -2", 0.25),
    ("-2 ** -3", -0.125),
    ("(1 + 1) ** 2", 4),
    ("1 + 1 ** 2", 2),
    ("(1 + 2)! ** 2", 36),
    ("1! ** 2! ** 3! - 4! + 5!", 97),
    ("(1!+(2!+(3!+4!*(5*6))))", 729),
    ("(100 - (1 + 2)! ** 2) / 16", 4),
    ("2 ** (3 * (5! / 4! - 1) / 2)", 64)
])
def test_complex_op(a, expr, expected):
    assert a(expr) == expected