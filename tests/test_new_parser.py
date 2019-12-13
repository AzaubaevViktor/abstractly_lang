def test_new_parser(a):
    # _  := @space
    # __ := _+
    a("power_parser := a:number __ '**' __ b:number => @power(a, b)")
    assert a("2 ** 3") == 8


def test_new_op(a):
    a("expr |= a:expr __ '%)' __ b:expr => a * b - a - b")
    assert a("10 %) 20") == 170
