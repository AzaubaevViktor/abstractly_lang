import asyncio

from aiohttp import web

import socketio

sio = socketio.AsyncServer(async_mode='aiohttp')
app = web.Application()
sio.attach(app)


@sio.event
async def connect(*args):
    print('connect', args)


@sio.event
async def disconnect(*args):
    print("disconnect", args)


async def index(request):
    with open('latency.html') as f:
        return web.Response(text=f.read(), content_type='text/html')


@sio.event
async def ping_from_client(*args):
    print("ping", args)
    await sio.emit('pong_from_server')


# app.router.add_static('/static', 'static')
# app.router.add_get('/', index)


async def do():
    try:
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "localhost", 8080)
        await site.start()
        while True:
            await asyncio.sleep(1)

    except Exception:
        await site.stop()
        await runner.cleanup()
        await app.cleanup()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(do())
