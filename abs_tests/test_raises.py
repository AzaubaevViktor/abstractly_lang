from test.test import TestedService, raises


class TestRaises(TestedService):
    async def test_simple(self):
        with raises(ZeroDivisionError) as exc_info:
            self.logger.info(1 / 0)

        assert isinstance(exc_info.value, ZeroDivisionError)
        assert exc_info.type == ZeroDivisionError

    async def test_wrong(self):
        try:
            with raises(ZeroDivisionError) as exc_info:
                self.logger.info(1 / 1)

            assert False, "raises must be raise"

        except AssertionError:
            pass

    async def test_wrong_exc(self):
        try:
            with raises(12) as exc_info:
                self.logger.info(1 / 1)

            assert False, "raises must be raise"

        except AssertionError:
            pass

    async def test_other_exc(self):
        with raises(AssertionError) as exc_info_parent:
            with raises(ZeroDivisionError) as exc_info_child:
                raise TypeError()
            assert False, "child raises must be skip exception"

        assert exc_info_parent.type is AssertionError
        assert isinstance(exc_info_parent.value, AssertionError)
