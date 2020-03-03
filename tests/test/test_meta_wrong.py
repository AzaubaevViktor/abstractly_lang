import pytest

from test.test import TestedService


def test_not_async():
    with pytest.raises(TypeError):
        class X(TestedService):
            def test_x(self):
                assert False, "NEVER CALL"
