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
