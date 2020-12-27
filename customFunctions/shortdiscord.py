import asyncio

import discord
import logging
import typing
from discord.ext import commands
# Logging
from discord.ext.commands import MissingPermissions

logger = logging.getLogger('own_functions')


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
