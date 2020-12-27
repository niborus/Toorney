print("Preparing the internal System.")

import discord
import logging
from discord.ext import commands

import Extensions
from config import SECRETS, STATICS
from customFunctions import boot, discord_oauth2
import translate
from BotNameBot import BotNameBot

# Logging
print(" Set up internal Variables")
handler = logging.FileHandler(filename = STATICS.LOG_FILE, encoding = 'utf-8', mode = 'w')
handler.setFormatter(logging.Formatter('%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s'))

logger_d = logging.getLogger('discord')
logger_d.setLevel(logging.INFO)
logger_d.addHandler(handler)

logger_o = logging.getLogger('own_functions')
logger_o.setLevel(logging.DEBUG)
logger_o.addHandler(handler)

logger_p = logging.getLogger('psql')
logger_p.setLevel(logging.INFO)
logger_p.addHandler(handler)

logger_l = logging.getLogger('loop')
logger_l.setLevel(logging.INFO)
logger_l.addHandler(handler)

intents = discord.Intents.default()
intents.members = True  # Subscribe to the privileged members intent.
intents.presences = True
intents.typing = False
intents.bans = False
intents.invites = False

bot = BotNameBot(command_prefix = commands.when_mentioned_or(STATICS.PREFIX), description = STATICS.DESCRIPTION,
                 status = discord.Status.dnd, owner_id = STATICS.OWNER_ID,
                 activity = discord.Game(name = "Booting"), intents = intents,
                 allowed_mentions = discord.AllowedMentions(everyone = False, users = False, roles = False))


@bot.event
async def on_ready():
    c = len(bot.guilds)
    boot.console_start(discord.__version__, c)
    await bot.change_presence(activity = discord.Game(name = "type s.help"))


@bot.event
async def on_guild_join(guild: discord.Guild):
    await discord_oauth2.execute_webhook_by_id \
        (STATICS.INFORMATION_WEBHOOK[0], STATICS.INFORMATION_WEBHOOK[1],
         content = ":green_circle: [{}] I was added to guild **{}**."
         .format(len(bot.guilds), discord.utils.escape_markdown(guild.name)))


@bot.event
async def on_guild_remove(guild: discord.Guild):
    await discord_oauth2.execute_webhook_by_id \
        (STATICS.INFORMATION_WEBHOOK[0], STATICS.INFORMATION_WEBHOOK[1],
         content = ":red_circle: [{}] I was removed from guild **{}**."
         .format(len(bot.guilds), discord.utils.escape_markdown(guild.name)))


# Import all Commands
print(" Load extensions")
for ex in Extensions.loadable():
    bot.load_extension(ex)

# Create Pot for Help-Strings
translate.create_help_text_pot(bot)

print("Preparing the external System.")
bot.run(SECRETS.TOKEN)
