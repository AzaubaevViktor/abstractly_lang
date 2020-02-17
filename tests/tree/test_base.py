def test_base():
    a1 = Node()
    a2 = Node()

    a1.link(a2)

    assert a1.linked(a2)
