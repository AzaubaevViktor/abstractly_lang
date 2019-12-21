from parser import CharParser, OrParser


def test_lrec_eq():
    x = OrParser(CharParser('x'))
    x |= x & CharParser('y')

    assert x is x
    assert x == x
    assert hash(x) == hash(x)

    print(x)


def test_lrec_eq_other():
    x = OrParser(CharParser('x'))
    x |= x & CharParser('y')

    y = OrParser(CharParser('x'))
    y |= y & CharParser('y')

    assert x is not y
    assert x == y
    assert hash(x) == hash(y)

    print(x)
    print(y)
