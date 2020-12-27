import logging
import sys
import traceback

import aiohttp
from discord import AsyncWebhookAdapter
from discord import Webhook
from discord.ext import commands
from discord.ext.commands.errors import *
from discord.errors import *
from CustomErrors import GlobalMute, UserBanned, UserIsBot, CancelCommandSilent
from config.SECRETS import PANIC_WEBHOOK
from ToorneyBot import ToorneyBot
from customFunctions.shortdiscord import sanitize

logger = logging.getLogger("discord")


def setup(bot: ToorneyBot):
    @bot.event
    async def on_command_error(ctx: commands.Context, err):
        translate = bot.translate.get_t_by_ctx(ctx)
        _ = translate.gettext
        n_ = translate.ngettext

        # if command has local error handler, return
        if hasattr(ctx.command, 'on_error'):
            return

        # get the original exception
        err = getattr(err, 'original', err)

        # Prepared_Text:
        class t:
            support_server = \
                _("If you don't think, you made a mistake, please create a new issue ({link}).") \
                    .format(link = "https://github.com/niborus/Toorney/issues")

        # List with possible errors and the handling level of those errors

        class Errors:
            silent = (GlobalMute, UserIsBot, DisabledCommand, CancelCommandSilent)
            debug = (CommandOnCooldown,)
            info = (CheckFailure, MissingRequiredArgument, CommandNotFound, BadArgument, BadUnionArgument,
                    NoPrivateMessage, NotOwner, MissingPermissions, UserBanned, PrivateMessageOnly,
                    BotMissingPermissions)
            warnings = (CommandNotFound, Forbidden, NotFound)
            error = ()
            critical = ()

        err_type = type(err)
        # Logging the error
        if isinstance(err, Errors.critical):
            logger.critical("".join(traceback.format_exception(type(err), err, err.__traceback__)))
        elif isinstance(err, Errors.error):
            logger.error("".join(traceback.format_exception(type(err), err, err.__traceback__)))
        elif isinstance(err, Errors.warnings):
            logger.warning("".join(traceback.format_exception(type(err), err, err.__traceback__)))
        elif isinstance(err, Errors.info):
            logger.info(err)
        elif isinstance(err, Errors.debug):
            logger.debug(err)
        elif isinstance(err, Errors.silent):
            pass
        else:
            # Special treatment HTTP-Exception:
            if isinstance(err, HTTPException):
                logger.error("{} - {} - {} - {}\n  {}".format(err, err.status, err.text, err.code,
                                                              "".join(traceback.format_exception(type(err), err,
                                                                                                 err.__traceback__))))
            else:
                logger.error("".join(traceback.format_exception(type(err), err, err.__traceback__)))

            await ctx.send(_(
                "Something went terrible wrong while doing this.\nPlease reach out for the "
                "Bot-Support (https://github.com/niborus/Toorney/issues)."))

        # User Replies
        # Command silently Canceled:
        if isinstance(err, CancelCommandSilent):
            pass

        # Command Errors
        elif isinstance(err, (NotOwner,)):
            await ctx.send(_(":no_entry: No. I wan't do this for you. But can I do something else?"))
        elif isinstance(err, (DisabledCommand,)):
            await ctx.send(_(":no_entry: This command has been disabled for security reasons."))
        elif isinstance(err, PrivateMessageOnly):
            await ctx.send(_("This command can only be used in private messages."))
        elif isinstance(err, NoPrivateMessage):
            await ctx.send(_("This command cannot be used in private messages."))
        elif isinstance(err, (MissingPermissions, BotMissingPermissions)):
            missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in err.missing_perms]
            if len(missing) > 2:
                fmt = '{}, and {}'.format(", ".join(missing[:-1]), missing[-1])
            else:
                fmt = ' and '.join(missing)

            if isinstance(err, MissingPermissions):
                msg = n_(
                    "You are missing {0} permission to run this command.",
                    "You are missing {0} permissions to run this command.",
                    len(err.missing_perms)
                )
            else:
                if 'send_messages' in err.missing_perms:
                    return
                else:
                    msg = n_(
                        "Bot requires {0} permission to run this command.",
                        "Bot requires {0} permissions to run this command.",
                        len(err.missing_perms)
                    )

            await ctx.send(msg.format(fmt))

        elif isinstance(err, (MessageNotFound, MemberNotFound, UserNotFound, ChannelNotFound, RoleNotFound,
                              EmojiNotFound)):
            err_text = {
                MessageNotFound: _("I could not find the message `{argument}`."),
                MemberNotFound: _("I could not find the member `{argument}`."),
                UserNotFound: _("I could not find the user `{argument}`."),
                ChannelNotFound: _("I could not find the channel `{argument}`."),
                RoleNotFound: _("I could not find the role `{argument}`."),
                EmojiNotFound: _("I could not find the emoji `{argument}`."),
            }
            for possible_type in err_text.keys():
                if isinstance(err, possible_type):
                    await ctx.send(err_text[possible_type].format(argument = sanitize(err.argument)))
                    break
        elif isinstance(err, ChannelNotReadable):
            pass
        elif isinstance(err, (CommandOnCooldown,)):
            await ctx.send(_(":no_entry: Not so fast. Try again in %s second(s).") % str(int(err.retry_after) + 1))
        elif isinstance(err, (CheckFailure,)):
            await ctx.send(_(":no_entry: You are not allowed to do this."))
        elif isinstance(err, (MissingRequiredArgument, BadArgument, BadUnionArgument)):
            await ctx.send(
                _(":question: The Usage of that command is: `{0.prefix}{0.command.qualified_name} {0.command.usage}`")
                    .format(ctx))

        # HTTP Errors
        elif isinstance(err, Forbidden):
            await ctx.send(_("I don't have all permissions to do this!\n{0.support_server}").format(t))
        elif isinstance(err, NotFound):
            await ctx.send(_("At least one of the resources doesn't exist.\n{0.support_server}").format(t))

    @bot.event
    async def on_error(event, *args, **kwargs):
        exc = sys.exc_info()
        logger.error("{} raised an error:".format(event), exc_info = exc)

        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(PANIC_WEBHOOK, adapter = AsyncWebhookAdapter(session))
            try:
                msg = '`{}` raised an Error: `{}: {}`'.format(event, exc[0], exc[1])
            except:
                msg = '`{}` raised an Error'.format(event)

            await webhook.send(msg)
