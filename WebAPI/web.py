from aiohttp import web
from discord import Client


class Web:
    def __init__(self, client: Client):
        self.port = 8080
        self.task = client.loop.create_task(self._api())
        self._is_closed = False
        self.app = web.Application(loop = client.loop)
        self.routes = web.RouteTableDef()
        self._webserver: web.TCPSite

    async def _api(self):
        runner = web.AppRunner(self.app)
        self.app.add_routes(self.routes)
        await runner.setup()
        self._webserver = web.TCPSite(runner, '0.0.0.0', self.port)
        await self._webserver.start()

    async def close(self):
        """This function is a coroutine.

        Closes all connections.
        """
        if self._is_closed:
            return
        else:
            await self._webserver.stop()
            self.task.cancel()
            self._is_closed = True

    def add_routes(self, routes):
        self.app.add_routes(routes)

    def add_route(self, routes):
        self.app.add_routes([routes])
