""" ABS-38 """

from service import Message, handler
from test import TestedService


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
    @handler
    async def simple(self):
        return 1

    @handler
    async def simple_arg(self, x):
        return x

    @handler
    async def multi_arg(self, x, y, z):
        return x, y, z

    @handler
    async def simple_args(self, *args):
        return args

    @handler
    async def arg_args_start(self, *x, y, z):
        return x, y, z

    @handler
    async def arg_args_mid(self, x, *y, z):
        return x, y, z

    @handler
    async def arg_args_end(self, x, y, *z):
        return x, y, z

    @handler
    async def simple_kwarg(self, x=1):
        return x

    @handler
    async def simple_kwargs(self, **kwargs):
        return kwargs

    @handler
    async def args_kwargs(self, *args, **kwargs):
        return args, kwargs

    @handler
    async def all(self, x, *y, z, kx=1, ky=3, **kwargs):
        return x, y, z, kx, ky, kwargs

    @handler
    async def get_context(self, _ctx):
        return _ctx

    @handler(M1)
    async def use_m1(self, _ctx):
        assert isinstance(_ctx.message, M1)

        return _ctx.message.value

    @handler(M2, M3)
    async def use_m2_m3(self, _ctx):
        assert isinstance(_ctx.message, M2) or isinstance(_ctx.message, M3)

        return _ctx.message.value
