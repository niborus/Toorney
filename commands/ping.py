import time
from discord.ext import commands


def setup(bot):
    @bot.command(name = "ping", usage = "")
    @commands.cooldown(3, 5.0, type = commands.BucketType.user)
    async def ping(ctx: commands.Context):
        """Measure the latency of the Bot."""
        _ = bot.translate.get_t_by_ctx(ctx).gettext
        ping_text = _(":ping_pong: Pong!\n"
                      "Heartbeat: ``{heartbeat}``\n"
                      "Reaction Time: ``{reaction_time}``{fault_star}\n"
                      "Message Circuit: ``{roundabout}``\n\n{fault_text}")
        heartbeat = '{:.2f}ms'.format(ctx.bot.latency * 1000)
        start_time = time.perf_counter()
        message = await ctx.send(ping_text.format(heartbeat = heartbeat, reaction_time = '...', roundabout = '...',
                                                  fault_star = '', fault_text = ''))
        end_time = time.perf_counter()
        if (ctx.message.id & 0x3FF000) == (message.id & 0x3FF000):
            fault_star, fault_text = '', ''
        else:
            fault_star, fault_text = '\\*', _('\\**Measurement errors possible*')

        await message.edit(content = ping_text.format(
            heartbeat = heartbeat,
            reaction_time = '{}ms'.format((message.id >> 22) - (ctx.message.id >> 22)),
            roundabout = '{:.2f}ms'.format((end_time - start_time) * 1000),
            fault_star = fault_star, fault_text = fault_text
        ))
