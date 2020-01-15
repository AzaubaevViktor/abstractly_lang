from line import Line


def test_comment(a):
    assert a("1 + 2  # test comment") == 3
    assert a("# Just comment") == None
