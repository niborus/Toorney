from discord.ext import commands


class GlobalMute(commands.CommandError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return "GlobalMute is activated."


class UserBanned(commands.CommandError):
    def __init__(self, user_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = user_id

    def __str__(self):
        return "User {} is banned from the Bot".format(self.user_id)


class UserIsBot(commands.CommandError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return "User {} is a bot."


class ToManyRowsChanged(Exception):
    def __init__(self, expected, received, *args):
        super().__init__(*args)
        self.expected = expected
        self.received = received

    def __str__(self):
        return f"Too many Rows Changed. Expected: {self.expected}, Received: {self.received}"


class CancelCommandSilent(commands.CommandError):
    """Exception raised to cancel a Command. This should be done silently."""


class ToornamentNotFound(commands.BadArgument):
    """Raised if the Toornament ID cant be figured out."""
    def __init__(self, argument):
        self.argument = argument
        super().__init__('Toornament "{}" not found.'.format(argument))
