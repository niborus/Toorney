import discord, logging, typing, Extensions
from discord.ext import commands

logger = logging.getLogger('discord')


def setup(bot):

    @bot.group(name="extension", usage="", aliases=["ext"], hidden = True)
    @commands.is_owner()
    @commands.cooldown(1, 3.0, type=commands.BucketType.user)
    async def extensions_cmd(ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Please us a subcommand: \n"
                           "`list`\n"
                           "`(un)load <Extension> ['-e' for error message]`\n"
                           "`reload (<Extension>/'*' for all) ['-e' for error message]`")

    @extensions_cmd.command(name="list", usage="", aliases=["show"])
    async def extensions_show(ctx: commands.Context):
        """Show loaded extensions."""

        # Will Contain the Name of the extension.
        # Mod1 if extension in files
        # Mod2 if extension loaded
        extensions = {}

        for ex in Extensions.all_extensions():
            extensions[ex] = 1

        for ex in bot.extensions.keys():
            extensions[ex] = extensions.get(ex, 0) + 2

        ret_string = ""
        for ex in extensions:
            if extensions[ex] is 3:
                # Command is loaded and saved
                ret_string += ":white_check_mark:"
            elif extensions[ex] is 1:
                # Command is unloaded and saved
                ret_string += ":no_entry:"
            elif extensions[ex] is 2:
                # Command is loaded and unsaved
                ret_string += ":warning:"
            else:
                # Command is probably unloaded and unsaved
                # This should not happen
                ret_string += ":grey_question:"

            ret_string += " {}\n".format(ex)

        embed = discord.Embed(title="Extensions", description=":white_check_mark: - Command is loaded and saved\n"
                                                              ":no_entry: - Command is unloaded and saved\n"
                                                              ":warning: - Command is loaded and unsaved\n"
                                                              ":grey_question: - Something else. (Should never happen)")
        embed.add_field(name="Extensions", value=ret_string)

        await ctx.send(embed=embed)

    @extensions_cmd.command(name="load", usage="<Extension> ['-e' for error message]", aliases=["add"])
    async def extensions_load(ctx: commands.Context, extension: str, show_error: typing.Optional[str]):
        """Load an extension."""
        try:
            bot.load_extension(extension)
            Extensions.remove_from_unloaded(extension)
        except Exception as err:
            logger.warning("Failed to load extension {}".format(extension), exc_info=True)
            if show_error == "-e":
                await ctx.send("Failed to load extension {}\n{}".format(extension, err))
            else:
                await ctx.send("Failed to load extension {}".format(extension))
        else:
            logger.info("Load extension {}".format(extension))
            await ctx.send("Successfully loaded extension {}".format(extension))

    @extensions_cmd.command(name="unload", usage="<Extension> ['-e' for error message]", aliases=["remove"])
    async def extensions_unload(ctx: commands.Context, extension: str, show_error: typing.Optional[str]):
        """Unload an extension."""
        try:
            bot.unload_extension(extension)
            Extensions.add_to_unloaded(extension)
        except Exception as err:
            logger.warning("Failed to unload extension {}".format(extension), exc_info=True)
            if show_error == '-e':
                await ctx.send("Failed to unload extension {}\n{}".format(extension, err))
            else:
                await ctx.send("Failed to unload extension {}".format(extension))
        else:
            logger.info("Unload extension {}".format(extension))
            await ctx.send("Successfully unloaded extension {}".format(extension))

    @extensions_cmd.command(name="reload", usage="(<Extension>/'*' for all) ['-e' for error message]",
                            aliases=["update"])
    async def extensions_reload(ctx: commands.Context, extension: str, show_error: typing.Optional[str]):
        """Reload an extension."""
        if extension != "*":
            try:
                bot.reload_extension(extension)
            except Exception as err:
                logger.warning("Failed to reload extension {}".format(extension), exc_info=True)
                if show_error == "-e":
                    await ctx.send("Failed to reload extension {}\n{}".format(extension, err))
                else:
                    await ctx.send("Failed to reload extension {}".format(extension))
            else:
                logger.info("Reload extension {}".format(extension))
                await ctx.send("Successfully reloaded extension {}".format(extension))
        else:
            e_list = []
            old_extensions = bot.extensions.copy()
            for e in old_extensions:
                try:
                    bot.reload_extension(e)
                except Exception as err:
                    logger.warning("Failed to reload extension {}".format(e), exc_info=True)
                    if show_error == "-e":
                        e_list.append(":x: {} - {}".format(e, err))
                    else:
                        e_list.append(":x: {}".format(e))
                else:
                    logger.info("Reload extension {}".format(e))
                    e_list.append(":ballot_box_with_check: {}".format(e))

            e_list.sort()
            ret_string = ""

            for i in e_list:
                if len(i) + len(ret_string) + 2 > 1950:
                    await ctx.send(ret_string)
                    ret_string = ""
                ret_string += i + "\n"
            await ctx.send(ret_string)
