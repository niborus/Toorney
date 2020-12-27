import logging

from discord.ext import commands

from BotNameBot import BotNameBot
from CustomErrors import UserBanned, GlobalMute, UserIsBot

logger = logging.getLogger("discord")


def setup(bot: BotNameBot):
    # Initialisiere das Kern-Programm

    @bot.check
    async def is_allowed(ctx: commands.Context):
        """Check, if a user is allowed to invoke a command
        :return False if the user isn't allowed
        :return True if the User is allowed"""

        if ctx.bot.owner_id == ctx.author.id:
            return True

        if ctx.author.bot:
            raise UserIsBot()

        # Kontrolliere, ob ein globaler permanenter ID-Ban vorliegt
        if ctx.author.id in bot.safety_settings.user_blacklist:
            raise UserBanned(user_id = ctx.author.id)

        if bot.safety_settings.global_mute:
            await ctx.send(":no_entry: We temporary deactivated the bot for security reasons. Please try again later.")
            raise GlobalMute

        return True
