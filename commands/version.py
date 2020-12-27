import discord
from config import STATICS
import sys
from discord.ext import commands


def setup(bot):
    @bot.command(name = "version", usage = "")
    @commands.cooldown(2, 5, type = commands.BucketType.user)
    async def version(ctx: commands.Context):
        """Show the Version of the Bot"""

        embed = discord.Embed(title = "Version", color = 0x797979)
        embed.add_field(name = "Bot", value = STATICS.BOT_VERSION, inline = False)
        embed.add_field(name = "discord.py", value = discord.__version__, inline = False)
        embed.add_field(name = "Python", value = sys.version.split(" ")[0], inline = False)
        await ctx.send(embed = embed)
