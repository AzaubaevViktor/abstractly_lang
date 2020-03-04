from tests.test._abs_tests.test_hello import Hello, HelloMsg


def test_run_simple(runner):
    msg = runner(Hello, HelloMsg())

    assert msg.result_nowait() == "Hello, world!"
