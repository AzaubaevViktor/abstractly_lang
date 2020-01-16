from parser import CharParser, OrParser


def test_char_iter():
    x = CharParser('x')

    assert list(x) == [CharParser('x')]


def test_or_iter():
    x = CharParser('x')
    y = CharParser('y')
    z = x | y

    assert list(z) == [z, x, y]


def test_or_and_iter():
    x = CharParser('x')
    y = CharParser('y')
    z = CharParser('z')
    a = OrParser((x | y) & z)

    assert set(a) == {a, (x | y) & z, x, y, (x | y), z}

    a |= z & a

    sa = set(a)
    for _ in sa:
        print(_)

    assert sa == {a, (x | y), z, x, y, z & a}


