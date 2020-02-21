""" ABS-38 """

from service import Message, handler
from test import TestedService, raises


class M0(Message):
    def __init__(self, value):
        super().__init__()
        self.value = value


class M1(M0):
    pass


class M2(M0):
    pass


class M3(M0):
    pass


class TestHandlerMethods(TestedService):
    @classmethod
    async def simple(cls):
        return 1

    async def test_simple(self):
        assert 1 == await self.simple()
        assert 1 == await self.__class__.simple()

    @handler
    async def simple_arg(self, x):
        return x

    async def test_simple_arg(self):
        assert 5 == await self.simple_arg(5)
        assert 5 == await self.__class__.simple_arg(5)

    @handler
    async def multi_arg(self, x, y, z):
        return x, y, z

    async def test_multi_arg(self):
        assert (1, 2, 3) == await self.multi_arg(1, 2, 3)
        assert (1, 2, 3) == await self.__class__.multi_arg(1, 2, 3)

    @handler
    async def simple_args(self, *args):
        return args

    async def test_simple_args(self):
        assert (1, 2, 3) == await self.multi_arg(1, 2, 3)
        assert tuple() == await self.multi_arg()
        assert tuple(range(10)) == await self.multi_arg(*range(10))
        assert tuple(range(10)) == await self.__class__.multi_arg(*range(10))

    @handler
    async def arg_args_start(self, *x, y, z):
        return x, y, z

    async def test_arg_args_start(self):
        assert ((1, 2), 3, 4) == await self.arg_args_start(1, 2, y=3, z=4)
        assert (tuple(), 3, 4) == await self.arg_args_start(y=3, z=4)
        assert ((1, 2, 3, 4), 3, 4) == await self.arg_args_start(1, 2, 3, 4, y=3, z=4)

    @handler
    async def arg_args_mid(self, x, *y, z):
        return x, y, z

    @handler
    async def arg_args_end(self, x, y, *z):
        return x, y, z

    @handler
    async def simple_kwarg(self, x=10):
        return x

    async def test_simple_kwarg(self):
        assert 10 == await self.simple_kwarg(10)
        assert 10 == await self.simple_kwarg()
        assert 20 == await self.simple_kwarg(x=20)
        assert 10 == await self.__class__.simple_kwarg()

    @handler
    async def simple_kwargs(self, **kwargs):
        return kwargs

    async def test_simple_kwargs(self):
        assert {} == await self.simple_kwargs()
        assert {} == await self.__class__.simple_kwargs()
        assert {'a': 10} == await self.__class__.simple_kwargs(a=10)
        assert {'a': 10, 'b': 12} == await self.__class__.simple_kwargs(a=10, b=12)

    @handler
    async def args_kwargs(self, *args, **kwargs):
        return args, kwargs

    async def test_args_kwargs(self):
        assert tuple(), {} == await self.args_kwargs()
        assert tuple(), {} == await self.__class__.args_kwargs()
        assert (1, 2, 3), {} == await self.__class__.args_kwargs(1, 2, 3)
        assert tuple(), {'x': 4, 'y': 5, 'z': 6} == await self.__class__.args_kwargs(x=4, y=5, z=6)
        assert (1, 2, 3), {'x': 4, 'y': 5, 'z': 6} == await self.__class__.args_kwargs(1, 2, 3, x=4, y=5, z=6)

    @handler
    async def all(self, x, *y, z, kx=1, ky=3, **kwargs):
        return x, y, z, kx, ky, kwargs

    @handler
    async def get_context(self, _ctx=None):
        assert isinstance(_ctx, Context)

    @handler(M1)
    async def use_m1(self, value, _ctx=None):
        assert isinstance(_ctx.message, M1)
        assert _ctx.message.value is value

        return _ctx.message.value

    async def test_use_m1(self):
        assert 1 == await self.use_m1(1)
        assert 1 == await self.__class__.use_m1(1)
        assert 1 == await self.get(M1(1))
        message = await self.send(M1(1))
        assert 1 == await message.result()

    @handler(M1)
    async def wrong_m1(self, value, wtf_arg):
        assert False, "This cannot be execute"

    async def test_wrong_m1(self):
        with raises(Exception):
            await self.wrong_m1(1, 2)

        with raises(Exception):
            await self.__class__.wrong_m1(1, 2)

    @handler(M1)
    async def good_m1(self, value, wtf_arg=None):
        if value == 1:
            assert wtf_arg is None

        return value, wtf_arg

    async def test_good_m1(self):
        assert (1, None) == await self.wrong_m1(1)

        assert (2, 2) == await self.__class__.wrong_m1(2, 2)

        assert 10 == await self.send(M1(10))

    @handler(M2, M3)
    async def use_m2_m3(self, value, _ctx=None):
        assert isinstance(_ctx.message, M2) \
               or isinstance(_ctx.message, M3) \
               or (_ctx.message, _ctx.MessageDirectCall)

        assert _ctx.message.value is value

        return _ctx.message.value

    async def test_use_m2_m3(self):
        assert 1 == await self.use_m2_m3(1)
        assert 1 == await self.__class__.use_m2_m3(1)

        for klass in (M2, M3):
            assert 1 == await self.get(klass(1))
            message = await self.send(klass(1))
            assert 1 == await message.result()
