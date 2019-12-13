from tests.high_level._exec_ret import exec_ret


def test_exec_ret():
    assert exec_ret("1") == 1
    assert exec_ret("1 + 2 * 3") == 7
