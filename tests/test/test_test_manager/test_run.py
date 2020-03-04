from tests.test.at_project.abs_tests.atest_hello import Hello, HelloMsg


def test_run_simple(runner):
    msg = runner(Hello, HelloMsg())

    assert msg.result_nowait() == "Hello, world!"
