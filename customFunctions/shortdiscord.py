import asyncio

import discord
import logging
import typing
import toornament
from discord.ext import commands
from gettext import GNUTranslations
# Logging
from discord.ext.commands import MissingPermissions

logger = logging.getLogger('own_functions')

EMBED_FIELD_VALUE_LIMIT = 1024


class Errors:
    class NotOrganizer(commands.MissingPermissions):
        pass


async def globalmute_visibility(ctx: commands.Context, state):
    if state is True:
        await ctx.bot.change_presence(activity = discord.Game(name = "is muted."),
                                      status = discord.Status.do_not_disturb)
    if state is False:
        await ctx.bot.change_presence(activity = discord.Game(name = "a tournament."), status = discord.Status.online)


def has_channel_permission(member: discord.Member, channel: typing.Union[discord.TextChannel, discord.VoiceChannel],
                           raise_on_missing=False, me=False, **perms):
    """Checks if a Member has rights in an channel
    :keyword Taking Permissions
    :return True if Member has all permissions
    :return False if Member misses permission and raise_on_missing is False
    :raises MissingPermissions if Member misses permission and raise_on_missing is False"""

    invalid = set(perms) - set(discord.Permissions.VALID_FLAGS)
    if invalid:
        raise TypeError('Invalid permission(s): %s' % (', '.join(invalid)))

    permissions = channel.permissions_for(member)
    missing = [perm for perm, value in perms.items() if getattr(permissions, perm) != value]

    if not missing:
        return True
    else:
        if raise_on_missing:
            if me:
                raise commands.BotMissingPermissions(missing)
            else:
                raise commands.MissingPermissions(missing)
        else:
            return False


def has_guild_permissions(member: discord.Member, raise_on_missing=False, **perms):
    """Similar to :func:`has_channel_permission`, but operates on guild wide
    permissions instead of the current channel permissions.

    .. versionadded:: 1.3
    """

    invalid = set(perms) - set(discord.Permissions.VALID_FLAGS)
    if invalid:
        raise TypeError('Invalid permission(s): %s' % (', '.join(invalid)))

    permissions = member.guild_permissions
    missing = [perm for perm, value in perms.items() if getattr(permissions, perm) != value]

    if not missing:
        return True

    else:
        if raise_on_missing:
            raise MissingPermissions(missing)
        else:
            return False


async def wait_for_message_or_reaction(bot: commands.Bot, check_message, check_reaction, timeout):
    done, pending = await asyncio.wait([
        bot.wait_for('message', check = check_message, timeout = timeout),
        bot.wait_for('reaction_add', check = check_reaction, timeout = timeout + 1)
    ], return_when = asyncio.FIRST_COMPLETED)

    stuff = done.pop().result()
    for future in done:
        # If any exception happened in any other done tasks
        # we don't care about the exception, but don't want the noise of
        # non-retrieved exceptions
        future.exception()

    for future in pending:
        future.cancel()  # we don't need these anymore

    return stuff


def sanitize(s: str) -> str:
    return discord.utils.escape_mentions(discord.utils.escape_markdown(s))


def get_permission_slang(s: str):
    return s.replace('_', ' ').replace('guild', 'server').title()


def create_embed_from_tournament(tournament: toornament.Tournament, *, embed: typing.Optional[discord.Embed] = None,
                                 translation: typing.Optional[GNUTranslations] = None) -> discord.Embed:
    """Creates a Standard-Embed for a Tournament."""
    _ = translation.gettext if translation else lambda s: s

    if embed is None:
        embed = discord.Embed()

    embed.title = tournament.full_name or tournament.name
    embed.url = f"https://www.toornament.com/en_GB/tournaments/{tournament.id}"
    if tournament.logo:
        embed.set_thumbnail(url=tournament.logo.logo_medium)

    if tournament.online is None:
        online = None
    elif tournament.online:  # == True:
        online = _("Online")
    else:  # tournament.online: == False:
        online = _("Offline")

    if online:
        embed.add_field(name = _("Game"), value = f"{tournament.discipline}, {online}", inline = False)
    else:
        embed.add_field(name = _("Game"), value = f"{tournament.discipline}", inline = False)

    embed.add_field(name = _("Size"), value = str(tournament.size))

    possible_status = {
        "pending": _("Pending"),
        "running": _("Running"),
        "completed": _("Completed"),
    }
    embed.add_field(name = _('Status'), value = possible_status.get(tournament.status, _("Status unknown")))

    embed.set_footer(text = str(tournament.id))

    if isinstance(tournament, toornament.TournamentDetailed):
        if tournament.organization:
            embed.set_author(name = tournament.organization)

        embed.description = tournament.description

        if tournament.prize:
            embed.add_field(name = _("Price"), value = tournament.prize[:EMBED_FIELD_VALUE_LIMIT])

        contacts = []
        if tournament.discord:
            contacts.append(_("Discord: [{0}]({1})").format(tournament.discord.rsplit('/', 1)[1], tournament.discord))
        if tournament.contact:
            contacts.append(_("E-Mail Address: {0}").format(tournament.contact))
        if tournament.website:
            contacts.append(_("Website: [{0}]({1})").format(tournament.website))
        if contacts:
            embed.add_field(name = _("Contact"), value = "\n".join(contacts), inline = False)

    return embed
