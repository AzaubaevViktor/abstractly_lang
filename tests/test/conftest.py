from typing import Type, Callable

import pytest

from test.test import TestedService, TestInfo


@pytest.fixture(scope='session')
def finder() -> Callable[[Type[TestedService], str], TestInfo]:
    def _f(class_: Type[TestedService], name: str):
        assert isinstance(class_, type)
        assert issubclass(class_, TestedService)

        assert class_.__tests__

        # check types
        for test_info in class_.__tests__.values():
            assert isinstance(test_info, TestInfo)
            assert issubclass(class_, test_info.class_)

        # find

        test_info = class_.__tests__.get(name)
        if test_info:
            assert test_info.method_name == name
            return test_info

        names = [test_info.method_name for test_info in class_.__tests__.values()]

        assert False, f"Method {name} not found, try one of: " \
                      f"{names}"

    return _f
