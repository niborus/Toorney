from discord.ext import commands
import translate

from SafetySettings import SafetySettings


class ToorneyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set up Translation
        self.translate = translate.LookUpByID()

        self.safety_settings = SafetySettings()
