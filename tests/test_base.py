from parser import CharParser


def test_char_hash():
    assert hash(CharParser("x")) == hash(CharParser("x"))


def test_and_hash():
    x = CharParser("x")
    y = CharParser("y")

    a1 = x & y
    a2 = x & y

    assert hash(a1) == hash(a2)


def test_or_hash():
    x = CharParser("x")
    y = CharParser("y")

    a1 = x & y
    a2 = x & y

    assert hash(a1) == hash(a2)
