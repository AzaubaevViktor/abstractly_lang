from tests.conftest import exec_ret


def test_exec_ret():
    assert exec_ret("1") == 1
    assert exec_ret("1 + 2 * 3") == 7
