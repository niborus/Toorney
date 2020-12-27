import discord
from discord.ext import commands
from config import STATICS
from ToorneyBot import ToorneyBot


def setup(bot: ToorneyBot):
    @bot.command(name = "about")
    @commands.bot_has_permissions(embed_links = True)
    @commands.cooldown(2, 5.0, type = commands.BucketType.user)
    async def about(ctx):
        """Get information about the bot."""
        _ = bot.translate.get_t_by_ctx(ctx).gettext
        embed = discord.Embed(title = STATICS.BOT_NAME, url = "", description = STATICS.DESCRIPTION, color = 0x2553c5)
        contact_message = _("Do you want to make a suggestion or report a bug?\n"
                            "Visit us on https://github.com/niborus/Toorney")
        embed.add_field(name = _("Contact:"),
                        value = contact_message,
                        inline = False)
        await ctx.message.channel.send(embed = embed)
