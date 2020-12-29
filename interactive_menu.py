import asyncio, discord
from discord.ext import commands
from customFunctions.diverse import get_toornament_id_by_url


# Es gibt folgende Items:
# - Oberteil (C)
# - Unterteil
# - Kleid (C)
# - Kopfbedeckungen (C)
# - Accessoires (M)
# - Socken
# - Schuhe
# - Tasche
# - Gesichtsbemalung (Cx)
# Codes:
# - Design: MO-????-????-????
# - Creator: MA-????-????-????


class Canceled(Exception):
    """Get raised if user cancels the command."""

    def __init__(self, msg=None, *args, **kwargs):
        super(*args, **kwargs)
        self.msg = msg


class InvalidAnswer(Exception):

    def __init__(self, msg=None):
        if msg:
            self.msg = msg
        else:
            self.msg = "Das geht so nicht."


class AwaitResponse:
    def __init__(self, ctx: commands.Context):
        """Creates a new Dialog with the user.
        :param ctx The Context. This adds basic checks to the bot."""
        self.ctx = ctx
        self._ = ctx.bot.translate.get_t_by_ctx(ctx).gettext

    def _is_answer(self, message):
        return message.author == self.ctx.author and message.channel == self.ctx.channel

    async def await_response(self, check, timeout=300.0):
        """
        :returns Any
        :raises asyncio.TimeoutError
        :raises Canceled"""
        while True:
            msg = await self.ctx.bot.wait_for('message', timeout = timeout, check = self._is_answer)
            if msg.content is not None:
                if msg.content.lower() == 'cancel':
                    raise Canceled
            try:
                return await check(msg)
            except InvalidAnswer as err:
                await self.ctx.send(err.msg)

    async def yes_no(self, timeout=300.0):
        """Expect a `yes` or `no` from the user.
        :returns Boolean
        :raises asyncio.TimeoutError
        :raises Canceled"""

        async def check(msg):
            if msg.content.lower() in ('y', 'yes'):
                return True
            elif msg.content.lower() in ('n', 'no'):
                return False
            else:
                raise InvalidAnswer(self._("The Answer must be either `yes` or `no`."))

        return await self.await_response(check, timeout)

    async def multiple_choice(self, array, timeout=300.0):
        """Expect a element from the Set from the user.
        :returns str
        :raises asyncio.TimeoutError
        :raises Canceled"""

        array_lower = [element.lower() for element in array]

        async def check(msg):
            if msg.content.lower() in array_lower:
                return msg.content.lower()
            else:
                raise InvalidAnswer(discord.utils.escape_mentions(
                    self._("Please Choose one of the following Options: `{0}`").format('`, `'.join(array))
                ))

        return await self.await_response(check, timeout)

    async def string_with_max_length(self, max_char=60, timeout=300.0):
        """Expect a string with a max length from the user.
        :returns str
        :raises asyncio.TimeoutError
        :raises Canceled"""
        async def check(msg):
            if len(msg.content) > max_char:
                raise InvalidAnswer(self._("Don't use more than {max_char} Characters.").format(max_char = max_char))
            else:
                return msg.content

        return await self.await_response(check, timeout)

    async def toornament(self, timeout=300.0):
        """Expect a Toornament (Link or ID) from User.
        :returns Toornament ID
        :raises asyncio.TimeoutError
        :raises Canceled"""
        async def check(msg):
            potential_id = get_toornament_id_by_url(msg.content, raise_error = False)
            if not potential_id:
                raise InvalidAnswer(self._("This wasn't a valid URL or valid ID. Try again!"))
            else:
                return potential_id

        return await self.await_response(check, timeout)


class QuestionCatalog:
    """Catalog contains prepared Questions for many Situations.
    Must be initialized to send messages."""

    def __init__(self, ctx: commands.Context):
        self.ctx = ctx
        self._ = ctx.bot.translate.get_t_by_ctx(ctx).gettext
        self.response_handler = AwaitResponse(ctx)

    async def toornament(self, timeout=300.0):
        """Expect a Toornament (Link or ID) from User.
        :returns Toornament ID
        :raises asyncio.TimeoutError
        :raises Canceled"""
        await self.ctx.send(self._("Please provide a link or the ID of the toornament."))
        return await self.response_handler.toornament(timeout)

    async def multiple_choice_with_numbers(self, dict_with_options, description=None):
        """Expect a Toornament (Link or ID) from User.
        :returns Toornament ID
        :param dict_with_options A dict with ElementID, Public Text
        :param description An optional description for the Embed.
        :raises asyncio.TimeoutError
        :raises Canceled"""
