import discord
from discord.ext import commands
from config import STATICS
from BotNameBot import BotNameBot


def setup(bot: BotNameBot):
    @bot.command(name = "about")
    @commands.bot_has_permissions(embed_links = True)
    @commands.cooldown(2, 5.0, type = commands.BucketType.user)
    async def about(ctx):
        """Get information about the bot."""
        _ = bot.translate.get_t_by_ctx(ctx).gettext
        embed = discord.Embed(title = STATICS.BOT_NAME, url = "", description = STATICS.DESCRIPTION, color = 0x2553c5)
        contact_message = _("Do you need help, want to make a suggestion or report a bug?\n"
                            "[Join our Support-Server.](https://discord.gg/QFhEhpG)\n\n"
                            "Do you need to contact to developer per E-Mail?\nWrite me a private message with `s.mail`.")
        embed.add_field(name = _("Contact:"),
                        value = contact_message,
                        inline = False)
        await ctx.message.channel.send(embed = embed)

    @bot.command(name = "mail", hidden = True)
    @commands.dm_only()
    @commands.cooldown(1, 30.0, type = commands.BucketType.user)
    async def email_contact(ctx):
        """Get the E-Mail Address of the developer"""
        _ = bot.translate.get_t_by_ctx(ctx).gettext
        embed = discord.Embed(title = _("Contact the developer."), color = 0x2553c5,
                              description = _(
                                  "If you need help with the bot or want to make a suggestion, please make "
                                  "this on [our Support-Server](https://discord.gg/QFhEhpG).\n"
                                  "Use this E-Mail Address **only** for Bug-Reports and vulnerable messages.")
                              )
        embed.add_field(name = _("E-Mail Address:"), value = _("niborus@yunamio.de"))
        e_val = _("[0xBA853A5A53E8EDD1](https://keys.mailvelope.com/pks/lookup?op=get&search=niborus@yunamio.de)\n"
                  "Fingerprint:\n`1A7E DDE1 23BD 71FC C087 613D BA85 3A5A 53E8 EDD1`")
        embed.add_field(name = _("Encryption:"), value = e_val, inline = False)
        ht_val = _("If you are writing your E-Mails in a browser like Chrome, Firefox or Edge, you can use the open-"
                   "source plugin extension [Mailvelope](https://www.mailvelope.com/en).\n"
                   "Look up the website from [Jugendhackt](https://howtopgp.jugendhackt.de/#/) to get more information "
                   "and good software for other devices.")
        embed.add_field(name = _("How to encrypt:"), value = ht_val, inline = False)
        await ctx.send(embed = embed)

    @bot.command(name = "upcoming")
    @commands.bot_has_permissions(embed_links = True)
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    async def upcoming_field(ctx):
        """Get informed about upcoming changes from Supporter."""
        _ = bot.translate.get_t_by_ctx(ctx).gettext
        embed = discord.Embed(title = _("Upcoming Changes."), color = 0x2553c5, description = "")

        fc = _(
            "The FollowChannel Module was an alternative for Discords AnnouncementChannel for those developers, who "
            "couldn't afford a Game License. When Discord enabled the [Community-Servers]"
            "(https://support.discord.com/hc/de/articles/360047132851-Enabling-Your-Community-Server) "
            "for every server, they also enabled the AnnouncementChannel for every Server.\n"
            "Therefore, the FollowChannel Module from Supporter is no longer useful and will be removed from the Bot. "
            "There is a transition period, so you can set up a AnnouncementChannel and inform everyone about the changes.\n"
            "The FollowChannel Module, which include the commands `follow` and `publish` will be deactivated at "
            "**November 7, 2020**. This is the same date, when Discord will drop the support for the old domain "
            "*discordapp.com*.")
        embed.add_field(name = _("FollowChannel"), value = fc)

        await ctx.send(embed = embed)
