from typing import Type, Callable

import pytest

from test.test import TestedService, TestInfo


@pytest.fixture(scope='session')
def finder() -> Callable[[Type[TestedService], str], TestInfo]:
    def _f(class_: Type[TestedService], name: str):
        assert isinstance(class_, type)
        assert issubclass(class_, TestedService)

        assert class_.__tests__

        for test_info in class_.__tests__:
            assert isinstance(test_info, TestInfo)
            assert issubclass(class_, test_info.class_)

        for test_info in class_.__tests__:
            if test_info.method_name == name:
                return test_info

        assert False, f"Method {name} not found"

    return _f
