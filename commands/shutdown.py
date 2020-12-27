from discord.ext import commands
from BotNameBot import BotNameBot
from typing import Optional


def setup(bot: BotNameBot):
    @bot.command(name = "shutdown", usage = "[-f force]")
    @commands.is_owner()
    async def shutdown(ctx: commands.Context, flag: Optional[str]):
        """Shut down the Bot."""
        if flag != '-f':
            try:
                cog = bot.get_cog('OfflineCheck')
                await cog.message_all_remaining_people()
            except AttributeError:
                pass
            await ctx.send(":sleeping: Good night.")
        await bot.close()
