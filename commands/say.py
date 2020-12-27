import discord
from discord.ext import commands
from typing import Optional
from ToorneyBot import ToorneyBot


class Say(commands.Cog):
    """Make the Bot say something in a Channel."""

    def __init__(self, bot: ToorneyBot):
        self.bot = bot

    @commands.command(name = "say", usage = "[Channel] <Text>", hidden = True)
    @commands.has_guild_permissions(administrator = True)
    @commands.cooldown(2, 1, type = commands.BucketType.user)
    async def say(self, ctx: commands.Context, channel: Optional[discord.TextChannel] = None, *, text):
        """Say a text without letting the bot mention user, roles or everyone.
        You might still mention user, roles or everyone while sending the command."""
        if not channel:
            channel = ctx.channel
        if ctx.channel.id == channel.id and ctx.channel.permissions_for(ctx.me).manage_messages:
            await ctx.message.delete()
        await channel.send(text)

    @commands.command(name = "scream", usage = "[Channel] <Text>", hidden = True)
    @commands.has_guild_permissions(administrator = True)
    @commands.cooldown(2, 1, type = commands.BucketType.user)
    async def say_with_mention(self, ctx: commands.Context, channel: Optional[discord.TextChannel] = None, *, text):
        """Say an Text and mention user, roles or everyone while doing so."""
        if not channel:
            channel = ctx.channel
        if ctx.channel.id == channel.id and ctx.channel.permissions_for(ctx.me).manage_messages:
            await ctx.message.delete()
        await channel.send(text,
                           allowed_mentions = discord.AllowedMentions(everyone = True, roles = True, users = True))

    @commands.command(name = "edit", usage = "<message> <Text>", hidden = True)
    @commands.has_guild_permissions(administrator = True)
    @commands.cooldown(2, 1, type = commands.BucketType.user)
    async def say_with_mention(self, ctx: commands.Context, message: discord.Message, *, text):
        """Edit a message-"""
        await message.edit(content = text)


def setup(bot):
    bot.add_cog(Say(bot))
