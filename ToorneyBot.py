from discord.ext import commands
from toornament import AsyncViewerAPI
from config.SECRETS import ToornamentLogin
import translate
import WebAPI
from aiohttp import web

from SafetySettings import SafetySettings


class Web:
    def __init__(self, bot: commands.Bot):
        self.webhook_port = 8083
        self.task = bot.loop.create_task(self._api())
        self._is_closed = False
        self.app = web.Application(loop = bot.loop)
        self._webserver: web.TCPSite

    async def _api(self):
        runner = web.AppRunner(self.app)
        await runner.setup()
        self._webserver = web.TCPSite(runner, '0.0.0.0', self.webhook_port)
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


class ToorneyBot(WebAPI.Client, commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set up Translation
        self.translate = translate.LookUpByID()

        self.safety_settings = SafetySettings()

        self.viewer_api = AsyncViewerAPI(ToornamentLogin.api_key)

        self.web_api.port = 8083
