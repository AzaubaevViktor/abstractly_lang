import socketio
from aiohttp import web

from log import Log


class _SIOWrapper:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.logger = Log(f"Site:{self.host}:{self.port}")

        self.sio: socketio.AsyncServer = socketio.AsyncServer(async_mode="aiohttp")
        self._app: web.Application = web.Application()
        self.sio.attach(self._app)

        self._runner: web.AppRunner
        self._site: web.TCPSite

    async def run(self):
        self.runner = web.AppRunner(self._app)

        # web.run_app(), but manually
        await self.runner.setup()

        self.site = web.TCPSite(
            self.runner, self.host, self.port,
            shutdown_timeout=1
        )

        await self.site.start()
        self.logger.important("Server started!")

    async def stop(self):
        for ns, rooms in tuple(self.sio.manager.rooms.items()):
            self.logger.info(ns=ns)
            for room, sids in tuple(rooms.items()):
                for sid in tuple(sids.keys()):
                    self.logger.info(room=room, sid=sid)
                    await self.sio.disconnect(sid, ns)
        self.logger.debug("Stopping site")
        await self.site.stop()

        self.logger.debug("Stopping runner")
        await self.runner.cleanup()

        self.logger.debug("Stopping app")
        await self._app.cleanup()

        self.logger.info("Server stopped!")

    def on(self, event, handler=None, namespace=None):
        self.sio.on(event, handler=handler, namespace=namespace)
