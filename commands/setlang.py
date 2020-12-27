from discord.ext import commands
from ToorneyBot import ToorneyBot
from typing import Optional
from customFunctions.diverse import update_guild_setting


def setup(bot: ToorneyBot):
    @bot.command(name = "language", usage = "<language code>", aliases = ['lang'])
    @commands.cooldown(1, 3.0, commands.BucketType.guild)
    @commands.has_guild_permissions(manage_guild = True)
    async def set_language(ctx: commands.Context, language: Optional[str] = None):
        _ = bot.translate.get_t_by_ctx(ctx).gettext

        lang_list = [_("German"), _("English")]

        lang_names = {
            'de': 'de',
            'en': 'en',
            'german': 'de',
            'english': 'en',
            'deutsch': 'de',
            'englisch': 'en',
        }

        if not language or language.lower() not in lang_names.keys():
            await ctx.send(_("Please choose one of the following languages: {0}").format(', '.join(lang_list)))

        else:
            lang_code = lang_names[language.lower()]
            update_guild_setting(ctx.guild.id, {'language': lang_code})
            bot.translate.set(ctx.guild.id, lang_code)
            _ = bot.translate.get_t_by_ctx(ctx).gettext
            await ctx.send(_("I set the language to **English**!"))
