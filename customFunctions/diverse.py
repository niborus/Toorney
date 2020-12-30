import collections
import re
import toornament
import discord
from collections.abc import Iterable
from typing import Union
from CustomErrors import ToornamentNotFound

from customFunctions import shortsql


def ismention(text, checktype="all"):
    """Checks, if a string is a mention of a specific or general type."""

    class ret(object):

        type = None
        result = False
        id = None

    if text.startswith("<@!") and text.endswith(">"):
        ret.type = "user"
        id = text[3:-1]
    elif text.startswith("<@") and text.endswith(">"):
        ret.type = "user"
        id = text[2:-1]
    elif text.startswith("<#") and text.endswith(">"):
        ret.type = "channel"
        id = text[2:-1]
    elif text.startswith("<@&") and text.endswith(">"):
        ret.type = "role"
        id = text[3:-1]

    if ret.type is None:
        return ret
    else:
        if id.isdigit():
            ret.id = id
            if checktype == "all" or checktype == ret.type: ret.result = True

    return ret


def build_path_in_dict(original_dict: dict, path: list, final_type: type) -> dict:
    if type(original_dict) is not dict:
        original_dict = {}

    if path.__len__() > 1:
        original_dict[path[0]] = build_path_in_dict(original_dict.get(path[0], {}), path[1:], final_type)
    else:
        if type(original_dict.get(path[0])) is not final_type:
            original_dict[path[0]] = final_type()
    return original_dict


def insert_value_in_dict(original_dict: dict, path: list, final_value) -> dict:
    if type(original_dict) is not dict:
        original_dict = {}

    if path.__len__() > 1:
        original_dict[path[0]] = insert_value_in_dict(original_dict.get(path[0], {}), path[1:], final_value)
    else:
        original_dict[path[0]] = final_value
    return original_dict


def get_element_in_dic(original_dict: dict, path: list):
    if path.__len__() > 0:
        return get_element_in_dic(original_dict[path[0]], path[1:])
    else:
        return original_dict


def deep_update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = deep_update(d.get(k, {}), v)
        elif isinstance(v, list) and isinstance(d.get(k), list):
            d[k] = d[k] + v
        elif not (v is None and isinstance(d.get(k), list)):
            d[k] = v
    return d


def get_guild_setting(guild_id: int, settings: Union[str, Iterable]):
    """ Search the Database for Guild-Settings. Creates Row if Guild is not in Settings.
    :return Setting from the DB.
    :raises psycopg2.errors.UndefinedColumn if setting does not exist
    :param guild_id (int) ID of the Guild
    :param settings (Iterable[str] or Str) List of the Settings or the Setting"""

    multiple_settings = True

    if isinstance(settings, str):
        settings = (settings,)
        multiple_settings = False
    if not isinstance(settings, Iterable):
        raise ValueError("`settings` need to be str or Iterable.")

    q = f"SELECT {', '.join(settings)} FROM guild_settings WHERE guild_id = $1;"
    r = shortsql.sync_save_read(q, (guild_id,))

    if len(r) == 0:
        shortsql.sync_save_write("INSERT INTO guild_settings (guild_id) VALUES ($1);", (guild_id,), 1)
        r = shortsql.sync_save_read(q, (guild_id.__str__(),))

    if multiple_settings:
        return r[0]
    else:
        return r[0][0]


def update_guild_setting(guild_id: int, settings: dict) -> None:
    """ Update a Setting in the Database. If Guild does not exist, make entry.
    :return None.
    :raises psycopg2.errors.UndefinedColumn if setting does not exist
    :param guild_id (int) ID of the Guild
    :param settings (dict) List of the Setting_names with Setting"""

    if settings != {}:

        setting_names = []
        setting_values = []

        for k, v in settings.items():
            if not isinstance(k, str):
                raise ValueError('Setting names need to be str. Got %s.' % str(type(k)))
            setting_names.append(k)
            setting_values.append(str(v))

        setting_values.append(guild_id)

        q = f"UPDATE guild_settings SET {', '.join([s + '=%s' for s in setting_names])} WHERE guild_id = %s;"

        if shortsql.sync_save_write(q, setting_values, 1) == 0:
            q = f"INSERT INTO guild_settings ({', '.join(setting_names)}, guild_id)" \
                f"VALUES ({', '.join(['%s' for v in setting_values])})"

            shortsql.sync_save_write(q, setting_values, 1)

    else:
        shortsql.sync_save_write("insert into guild_settings (guild_id) values (%s) ON CONFLICT DO NOTHING;", (guild_id,), 1)


def get_toornament_id_by_url(url: str, raise_error=True):
    url = url.strip()

    if url.isdecimal():
        return int(url)

    match = re.search('tournaments/([0-9]+)', url, re.IGNORECASE)

    if not match:
        if raise_error:
            raise ToornamentNotFound(url)
        else:
            return None
    else:
        return int(match[1])


def create_embed_for_tournament(tournament: toornament.TournamentDetailed):

    embed = discord.Embed(name = tournament.name, colour = 0x0000ee)
    embed.description = "discipline: {0.discipline}\n" \
                        "full_name: {0.full_name}\n" \
                        "size: {0.size}\n" \
                        "participant_type: {0.participant_type}\n".format(tournament)
    if tournament.logo:
        embed.set_thumbnail(url = tournament.logo.original)

    return embed


def print_arguments(*args, **kwargs):
    print(
        "Invoked with {0} args:\n"
        "{1}\n"
        "and {2} kwargs\n"
        "{3}".format(len(args), '\n'.join(args), len(kwargs), '\n'.join([f'{k}: {v}' for k, v in kwargs.items()]))
    )
