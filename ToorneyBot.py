from discord.ext import commands
from toornament import AsyncViewerAPI
from config.SECRETS import ToornamentLogin
import translate

from SafetySettings import SafetySettings


class ToorneyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set up Translation
        self.translate = translate.LookUpByID()

        self.safety_settings = SafetySettings()

        self.viewer_api = AsyncViewerAPI(ToornamentLogin.api_key)
