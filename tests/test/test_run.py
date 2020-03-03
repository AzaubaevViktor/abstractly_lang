import asyncio

import pytest

from service import EntryPoint, Service, Message
from tests.test.abs_tests.test_hello import Hello, HelloMsg


@pytest.fixture(scope='session')
def runner():
    def _do_run(service: Service, message: Message):
        assert isinstance(service, Service) or (
            isinstance(service, type) and issubclass(service, Service)
        )

        async def run():
            entry_point = EntryPoint({
                service.__name__: [(
                    message.__class__.__name__,
                    dict(message)
                )]
            })
            await entry_point.warm_up()
            return await entry_point.run()

        return asyncio.run(run())

    return _do_run


def test_run_from_folder(runner):
    msgs = runner(Hello, HelloMsg())
    assert len(msgs) == 1
    msg = msgs[0]
    assert isinstance(msg, HelloMsg)

    assert msg.result_nowait() == "Hello, world!"

