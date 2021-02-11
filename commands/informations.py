import discord
from discord.ext import commands
from ToorneyBot import ToorneyBot
from customFunctions.diverse import get_toornament_id_by_url
from customFunctions.shortdiscord import create_embed_from_tournament


def setup(bot: ToorneyBot):

    @bot.command(name = "show", aliases = ['info', 'see'], usage='<tournament>')
    @commands.bot_has_permissions(embed_links = True)
    async def show_tournament(ctx: commands.Context, tournament_link: str):
        translation = bot.translate.get_t_by_ctx(ctx)
        _ = translation.gettext
        tournament_id = get_toornament_id_by_url(tournament_link)
        tournament = await bot.viewer_api.get_tournament(tournament_id)

        embed = discord.Embed(colour = ctx.me.colour)

        embed = create_embed_from_tournament(tournament, embed = embed, translation = translation)

        await ctx.send(embed = embed)

    @bot.command(name = "contact", usage = '<tournament>')
    @commands.bot_has_permissions(embed_links = True)
    async def show_tournament(ctx: commands.Context, tournament_link: str):
        translation = bot.translate.get_t_by_ctx(ctx)
        _ = translation.gettext
        tournament_id = get_toornament_id_by_url(tournament_link)
        tournament = await bot.viewer_api.get_tournament(tournament_id)

        embed = discord.Embed(colour = ctx.me.colour)

        embed.title = _("Contact for {toornament_name}").format(toornament_name = tournament.name)

        contacts = []
        if tournament.discord:
            contacts.append(_("Discord: [{0}]({1})").format(tournament.discord.rsplit('/', 1)[1], tournament.discord))
        if tournament.contact:
            contacts.append(_("E-Mail Address: {0}").format(tournament.contact))
        if tournament.website:
            contacts.append(_("Website: [{0}]({1})").format(tournament.website))
        if contacts:
            embed.description = '\n'.join(contacts)
        else:
            embed.description = _("No Contacts-Information available.")

        await ctx.send(embed = embed)
