import asyncio
from typing import Type, Callable, TypeVar, Union, List

import pytest

from service import Service, Message, EntryPoint
from test.test import TestedService, TestInfo


@pytest.fixture(scope='session')
def finder() -> Callable[[Union[List[TestInfo], Type[TestedService]], str], TestInfo]:
    def _f(class_: Union[List[TestInfo], Type[TestedService]], method_name: str):
        if isinstance(class_, type):
            assert issubclass(class_, TestedService)
            tests = class_.__tests__.values()

        else:
            isinstance(class_, list)
            tests = class_
            class_ = None

        assert tests

        # check types
        for test_info in tests:
            assert isinstance(test_info, TestInfo)
            if class_:
                assert issubclass(class_, test_info.class_)

        # find

        for test_info in tests:
            if test_info.method_name == method_name:
                return test_info

        names = [test_info.method_name for test_info in tests]

        assert False, f"Method {method_name} not found, try one of: " \
                      f"{names}"

    return _f


MSG = TypeVar("MSG", Message, Message)


@pytest.fixture(scope='session')
def runner() -> Callable[[Type[Service], MSG], MSG]:
    def _do_run(service: Type[Service], message: MSG) -> MSG:
        assert isinstance(service, Service) or (
            isinstance(service, type) and issubclass(service, Service)
        )

        async def run():
            entry_point = None
            try:
                entry_point = EntryPoint({
                    service.__name__: [(
                        message.__class__.__name__,
                        dict(message)
                    )]
                })
                await entry_point.warm_up()
                return await entry_point.run()
            finally:
                if entry_point:
                    await entry_point.cleanup()

        loop = asyncio.get_event_loop()
        msgs = loop.run_until_complete(run())
        assert len(msgs) == 1
        assert isinstance(msgs[0], Message)
        return msgs[0]

    return _do_run
