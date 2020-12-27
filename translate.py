import gettext, os
from typing import Optional, Union
from customFunctions import shortsql
from customFunctions import filehandling
from discord.ext import commands
from functools import wraps


def save_translate(original_function):
    @wraps(original_function)
    def wrapper(s: str):
        if s:
            return original_function(s)
        else:
            return s

    return wrapper


class LookUpByID:
    existing_languages = ["en", "de"]

    def __init__(self, lang_settings: Optional[dict] = None):

        # Compile Translation
        print("Compile mo-Files")
        for language in self.existing_languages:
            if language == 'en':
                continue
            os.system("msgfmt -o ./locale/{0}/LC_MESSAGES/interface.mo ./locale/{0}/LC_MESSAGES/interface.po".format(
                language))

        self.translation_instances = {}
        for language in self.existing_languages:
            trans = gettext.translation("interface", localedir = "locale", languages = [language], fallback = True)
            trans.gettext = save_translate(trans.gettext)
            self.translation_instances[language] = trans

        if lang_settings is None:
            lang_settings = {}

        result = shortsql.sync_save_read('SELECT guild_id, language FROM guild_settings;')
        for row in result:
            lang_settings[row[0]] = row[1]

        self.lang_settings = lang_settings

    def set(self, discord_id, lang):
        self.lang_settings[discord_id] = lang

    def get_t_by_id(self, discord_id):
        lang_code = self.lang_settings.get(discord_id, 'en')
        return self.translation_instances.get(lang_code, self.translation_instances['en'])

    def get_lc_by_id(self, discord_id):
        return self.lang_settings.get(discord_id)

    def get_t_by_ctx(self, ctx):
        discord_id = ctx.guild.id if ctx.guild else ctx.author.id
        return self.get_t_by_id(discord_id)


def add_to_pot(file, *strings):
    file_text = '''# SOME DESCRIPTIVE TITLE.
# Copyright (C) YEAR ORGANIZATION
# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
#
msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\\n"
"POT-Creation-Date: 2020-09-20 15:04+CEST\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: LANGUAGE <LL@li.org>\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: ENCODING\\n"
"Generated-By: SupporterBot\\n"

'''
    for s in strings:
        if not s:
            continue
        file_text += '\nmsgid '
        s = s.replace('\\', '\\\\').replace('"', '\\"')
        file_text += '"{0}"\n'.format('\\n"\n"'.join(s.split('\n')))
        file_text += 'msgstr ""\n'

    filehandling.write_file(file, file_text)


def get_help_text_from_command(set_help_text: set, commands_set: Union[set, dict]):
    if isinstance(commands_set, dict):
        commands_set = commands_set.values()
    for command in commands_set:
        set_help_text.update((command.help, command.usage, command.description))
        set_help_text.add(command.brief) if command.brief else None
        if type(command) == commands.Group:
            get_help_text_from_command(set_help_text, command.all_commands)


def create_help_text_pot(bot: commands.Bot):
    """Create .Pot for Commands and Cogs:"""
    # 'locale/pots/help_text.pot'
    set_help_text = set()
    # Adding Cogs
    for cog in bot.cogs.values():
        set_help_text.add(cog.description)
    # Adding Commands
    get_help_text_from_command(set_help_text, bot.commands)
    # Remove empty strings
    set_help_text.discard(None)
    set_help_text.discard("")
    # Create Pot
    add_to_pot('locale/pots/help_text.pot', *set_help_text)
