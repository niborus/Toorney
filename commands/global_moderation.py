from discord.ext import commands
import discord, typing
from ToorneyBot import ToorneyBot


class Globalmoderation(commands.Cog):

    def __init__(self, bot: ToorneyBot):
        self.bot = bot

    @commands.command(name = "globalban", usage = "<UserID>")
    @commands.is_owner()
    async def global_ban(self, ctx: commands.Context, user: typing.Union[discord.User, int]):
        """Bans a user permanently from using the Bot."""
        if isinstance(user, discord.User):
            user = user.id
        self.bot.safety_settings.global_user_ban()
        await ctx.send("I've banned the user with the ID: `%i`" % user)

    @commands.command(name = "globalunban", usage = "<UserID>")
    @commands.is_owner()
    async def global_unban(self, ctx: commands.Context, user: typing.Union[discord.User, int]):
        """Unbans a user permanently from using the Bot."""
        if isinstance(user, discord.User):
            user = user.id
        self.bot.safety_settings.global_user_unban(user)
        await ctx.send("I've unbanned the user with the ID: `%i`" % user)

    @commands.command(name = "globalmute", usage = "<on/off>")
    @commands.is_owner()
    async def globalmute_toggle(self, ctx: commands.Context, state: str):
        """If Globalmute is on, the Bot won't listen for commands (except owners)."""
        if state.lower() == "on":
            self.bot.safety_settings.toggle_globale_mute(True)
        elif state.lower() == "off":
            self.bot.safety_settings.toggle_globale_mute(False)
        else:
            raise commands.BadArgument()

        await ctx.send("Done!")


def setup(bot: ToorneyBot):
    bot.add_cog(Globalmoderation(bot))
