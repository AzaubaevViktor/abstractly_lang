from service import Service, handler


class Calculator(Service):
    @handler
    async def calc(self, a, b):
        return a + b
