import math


def test_simple_var(a):
    a("x = 12")
    assert a("x") == 12


def test_func(a):
    a("x = @factorial(10)")
    assert a("x") == math.factorial(10)


def test_func_var(a):
    a("x = 10")
    a("y = @factorial(x)")
    assert a("y") == math.factorial(10)


def test_func_var_expr(a):
    a("x = 9")
    a("y = @factorial(x + 1)")
    assert a("y") == math.factorial(10)


def test_func_func_var_expr(a):
    a("x = 3")
    a("y = @factorial(@factorial(x))")
    assert a("y") == math.factorial(math.factorial(3))
