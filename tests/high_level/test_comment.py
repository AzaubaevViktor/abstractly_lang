from line import Line


def test_comment(a):
    assert a("1 + 2  # test comment") == 3
    assert a("# Just comment") == None


def test_comment_parser():
    from main import _comment
    # print(list(_comment.parse(Line(""))))
    print(list(_comment.parse(Line("# test"))))
    print(list(_comment.parse(Line("#    sadf fd adsf adsf adsf "))))
    print(list(_comment.parse(Line("#    sadf fd adsf ### # # # # #  # adsf adsf "))))
