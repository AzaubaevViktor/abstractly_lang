import pytest

from line import Line


def test_eq():
    line1 = Line("123")
    line2 = Line("123")
    line3 = Line("234")

    assert line1 == line1
    assert line1 == line2
    assert line1 != line3
    assert line2 == line1
    assert line2 != line3
    assert line2 != line3
    assert line3 != line1
    assert line3 != line2
    assert line3 == line3

    assert line1 == "123"
    assert line2 == "123"
    assert line3 == "234"

    assert line1 != "234"
    assert line3 != "123"


def test_empty():
    assert Line("").empty
    assert not Line("123").empty


def test_get_item():
    orig_line = Line("hello world")

    new_line = orig_line[4]

    assert new_line.parent == orig_line
    assert new_line == 'o'
    assert new_line.pos == 4

    new_line = orig_line[:5]
    assert new_line.parent == orig_line
    assert new_line == "hello"
    assert new_line.pos == 0

    new_line = orig_line[1:5]
    assert new_line.parent == orig_line
    assert new_line == "ello"
    assert new_line.pos == 1


def test_line_str():
    print(Line("Hello, world!"))
    print(Line("Hello, world!")[4:7])


@pytest.mark.parametrize('raw_line', (
    'asdfasdasda',
    'asdfasdasda2',
    '0923n12j',
    '',
    'x',
    'xx',
    '💻👏⏰🧠'
))
def test_line_len(raw_line):
    assert len(raw_line) == len(Line(raw_line))

    mid = len(raw_line) // 2

    assert mid == len(Line(raw_line)[:mid])
    assert len(raw_line) - mid == len(Line(raw_line)[mid:])
