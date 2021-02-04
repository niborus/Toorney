from discord import Client as DPyClient
from .web import Web


class Client:
    def __init__(self, port=8080, *args, **kwargs):

        if not isinstance(self, DPyClient):
            raise TypeError("Web-API Client must be inherit next to discord.Client or commands.Bot")

        super().__init__(*args, **kwargs)

        self.web_api = Web(client = self, port=port)
