from parser import CharParser


def test_char_hash():
    assert hash(CharParser("x")) == hash(CharParser("x"))
