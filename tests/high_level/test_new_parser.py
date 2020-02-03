import pytest


def test_new_parser(a):
    # _  := @space
    # __ := _+
    a("__p = a:@number & __ & `^_^` & __ & b:@number")
    a("__fp = __p => @power(a, b)")
    a("@ |= __fp")
    assert a("2 ^_^ 3") == 8
    assert a("2 ^_^ 2 + 1") == 8


@pytest.mark.skip("Too long :(")
def test_new_op(a):
    a("@ |= a:@ & __ & `%)` & __ & b:@ => a * b - a - b")
    assert a("10 %) 20") == 170
