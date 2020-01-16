def test_new_parser(a):
    # _  := @space
    # __ := _+
    # TODO:
    a("@ |= a:@number & __ & `^_^` & __ & b:@number => @power(a, b)")
    assert a("2 ^_^ 3") == 8


def test_new_op(a):
    a("@ |= a:@ & __ & '%)' & __ & b:@ => a * b - a - b")
    assert a("10 %) 20") == 170
