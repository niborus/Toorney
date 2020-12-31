import discord
from asyncio import sleep
from aiohttp import ClientResponseError
from discord.ext import commands
from random import randint
from ToorneyBot import ToorneyBot
from typing import Optional
from interactive_menu import QuestionCatalog, AwaitResponse
from CustomErrors import CancelCommandSilent
from customFunctions.diverse import create_embed_for_tournament, print_arguments
import toornament

simple_cache = {}


class TournamentData:
    """Contains all Data about a Tournament."""

    def __init__(self, tournament: toornament.TournamentDetailed, stages: dict, groups: dict,
                 rounds: dict, matches: dict, participants: dict):
        """
        :param tournament: TournamentDetailed
        :param stages: dict[stage-id]: stage-object
        :param groups: dict[group-id]: group-object
        :param rounds: dict[round-id]: round-object
        :param matches: dict[match-id]: match-object
        :param participants: dict[participant-id]: participant-object
        """
        self.tournament = tournament
        self.stages = stages
        self.groups = groups
        self.rounds = rounds
        self.matches = matches
        self.participants = participants


async def clone_tournament(tournament_id, api: toornament.AsyncViewerAPI):
    """This Function Clones a Toornament.
    `tournament_data` contains the Data, that will be converted into a TournamentData-Instance later.."""
    tournament_data = {
        'tournament': await api.get_tournament(tournament_id),
        'stages': {stage.id: stage for stage in await api.get_stages(tournament_id)},
        'groups': {},
        'rounds': {},
        'matches': {},
        'participants': {},
    }

    async def get_all(element, max_range, api_function):
        """This function gets all Elements where a Range prevents to get all Elements."""
        i = 0
        while True:
            try:
                update_dict = {
                    entry.id: entry for entry in
                    await api_function(
                        tournament_id,
                        range = toornament.Range(i * max_range, (i + 1) * max_range - 1)
                    )
                }
                tournament_data[element].update(update_dict)
                if len(update_dict) < max_range:
                    break
                else:
                    i += 1
            # This is no pretty way, but is is the only way to handle Elements, where len(Elements) % max_range == 0
            except ClientResponseError as err:
                if err.status == 416:
                    break
                else:
                    raise err

    await get_all('participants', 50, api.get_participants)
    await get_all('groups', 50, api.get_groups)
    await get_all('rounds', 50, api.get_rounds)
    await get_all('matches', 128, api.get_matches_from_tournament)

    return TournamentData(**tournament_data)


class CloneType:
    @classmethod
    def get_placeholders(cls, element, tournament_data: TournamentData):
        """Takes a Element (like Player, Toornament, ) and the Data of the Tournament and creates a dict
        for placeholders."""
        return {
            'id': element.id
        }

    @classmethod
    def get_elements(cls, tournament_data: TournamentData):
        """:returns All Elements, that belong to the type of the CloneType unfiltered"""
        return []


class CloneTypeStages(CloneType):

    @classmethod
    def get_placeholders(cls, stage: toornament.Stage, tournament_data: TournamentData):
        placeholders = super().get_placeholders(stage, tournament_data)
        placeholders.update({
            'number': stage.number,
            'name': stage.name,
            'type': stage.type,
            'settings': stage.settings,
        })

        return placeholders

    @classmethod
    def get_elements(cls, tournament_data: TournamentData):
        return tournament_data.stages.values()


class CloneTypeGroups(CloneType):

    @classmethod
    def get_placeholders(cls, group: toornament.Group, tournament_data: TournamentData):
        placeholders = super().get_placeholders(group, tournament_data)
        placeholders.update({
            'number': group.number,
            'name': group.name,
            'settings': group.settings,
            'stage': CloneTypeStages.get_placeholders(tournament_data.stages[group.stage_id], tournament_data)
        })

        return placeholders

    @classmethod
    def get_elements(cls, tournament_data: TournamentData):
        return tournament_data.groups.values()


class CloneTypeRounds(CloneType):
    @classmethod
    def get_placeholders(cls, round: toornament.Round, tournament_data: TournamentData):
        placeholders = super().get_placeholders(round, tournament_data)
        placeholders.update({
            'stage': CloneTypeStages.get_placeholders(tournament_data.stages[round.stage_id], tournament_data),
            'group': CloneTypeGroups.get_placeholders(tournament_data.groups[round.group_id], tournament_data),
            'number': round.number,
            'name': round.name,
            'settings': round.settings,
        })

        return placeholders

    @classmethod
    def get_elements(cls, tournament_data: TournamentData):
        return tournament_data.rounds.values()


class CloneTypeMatches(CloneType):
    @classmethod
    def get_placeholders(cls, match: toornament.Match, tournament_data: TournamentData):
        placeholders = super().get_placeholders(match, tournament_data)
        round_placeholders = CloneTypeRounds.get_placeholders(tournament_data.groups[match.round_id], tournament_data)
        opponent_names = []
        for opponent in match.opponents:
            if opponent.participant:
                opponent_names.append(opponent.participant.name)
            else:
                opponent_names.append('TBD')
        placeholders.update({
            'stage': CloneTypeStages.get_placeholders(tournament_data.stages[match.stage_id], tournament_data),
            'group': CloneTypeGroups.get_placeholders(tournament_data.groups[match.group_id], tournament_data),
            'round': round_placeholders,
            'number': match.number,
            'type': match.type,
            'scheduled_datetime': match.scheduled_datetime,
            'name': 'M {0}.{1}'.format(round_placeholders['number'], match.number),
            'opponents_names_comma': ', '.join(opponent_names),
            'opponents_names_space': ' '.join(opponent_names),
            'opponents_names_linebreak': '\n'.join(opponent_names),
            'opponents_names_vs': ' vs. '.join(opponent_names),
        })

    @classmethod
    def get_elements(cls, tournament_data: TournamentData):
        return tournament_data.matches.values()


class CloneTypeParticipants(CloneType):

    @classmethod
    def get_placeholders(cls, participant: toornament.ParticipantPlayer, tournament_data: TournamentData):
        placeholder = super().get_placeholders(participant, tournament_data)
        placeholder.update({
            'name': participant.name,
            'custom_fields': participant.custom_fields,
        })
        return placeholder

    @classmethod
    def get_elements(cls, tournament_data: TournamentData):
        return tournament_data.participants.values()


class CloneTypeParticipantTeam(CloneTypeParticipants):
    @classmethod
    def get_placeholders(cls, participant: toornament.ParticipantTeam, tournament_data: TournamentData):
        placeholder = super().get_placeholders(participant, tournament_data)
        lineup_names = [players.name for players in participant.lineup]
        placeholder.update({
            'lineup_names_comma': ', '.join(lineup_names),
            'lineup_names_space': ' '.join(lineup_names),
            'lineup_names_linebreak': '\n'.join(lineup_names),
        })
        return placeholder


class CloneTypeCache:
    def __init__(self, clone_type, tournament_data: TournamentData, filter=None, sort_key=None, sort_reverse=False):
        self.clone_type = clone_type
        self.tournament_data = tournament_data
        self.filter = filter if filter else lambda element: True
        self.sort = {
            'key': sort_key if sort_key else lambda element: element.id,
            'reverse': sort_reverse
        }

    def get_prepared_list(self):
        unprepared_list = self.clone_type.get_elements(self.tournament_data)
        prepared_list = [element for element in unprepared_list if self.filter(element)]
        prepared_list.sort(**self.sort)
        return prepared_list
    
    def get_placeholders_for_element(self, element):
        return self.clone_type.get_placeholders(element, self.tournament_data)


class Clone:
    def __init__(self, guild: discord.Guild):
        self.dry = False
        self.reason = None
        self.guild = guild
        self.create_type = None
        self.name_pattern = "{i}"

    async def create(self, clone_type: CloneTypeCache):
        """Clones the Toornament to the server. Setting must be given before"""
        elements = clone_type.get_prepared_list()
        i = 1
        created_objects = {}
        for element in elements:
            placeholder = {'i': i}
            placeholder.update(clone_type.get_placeholders_for_element(element))
            created_objects[element] = await self.create_single(placeholder, element)
            i += 1
        return created_objects

    def create_arguments(self, placeholder, element) -> dict:
        """Creates the arguments needed for the `create_OBJETC` Method."""
        return {
            'name': self.name_pattern.format(**placeholder),
            'reason': self.reason
        }

    async def guild_create_object(self, *args, **kwargs):
        """Calls the according Discord-Function"""

    async def create_single(self, placeholder, element):
        """Creates a Single Instance, like one Role or one Channel"""
        arguments = self.create_arguments(placeholder, element)
        if not self.dry:
            await sleep(1.0)
            new_object = await self.guild_create_object(**arguments)
            return new_object
        else:
            print_arguments(**arguments)


class CloneRole(Clone):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_colour = 0
        self.mentionable = False
        self.hoist = False
        self.position = 1

    async def create(self, clone_type: CloneTypeCache):
        created_roles = await super().create(clone_type)
        if not self.dry and created_roles:
            # This fetches the roles from Discord and sends a fully ordered list with role-positions back.
            # The internal cache has huge problems to keep track of role positions.
            # Remember the IDs of the Roles created
            created_roles_ids = [role.id for role in created_roles.values()]
            # Fetch Roles from Discord
            all_roles = await self.guild.fetch_roles()
            # Sort roles by position
            all_roles.sort(key = lambda r: r.position)
            # Separate new roles from old roles
            all_roles_except_new_roles = [role for role in all_roles if role.id not in created_roles_ids]
            only_new_roles = [role for role in all_roles if role.id in created_roles_ids]
            # Reverse new roles, to let them appear in the correct order.
            only_new_roles.reverse()
            # `role_positions` is the argument, which will be given to guild.edit_role_positions
            # Key: Role, Value: Position (int)
            role_positions = {}
            # Counter keeps track of the position
            counter = 0

            # Insert old roles into `role_positions`
            for role in all_roles_except_new_roles[:self.position]:
                role_positions[role] = counter
                counter += 1
            # Remember where the old_roles were interrupted
            pointer_all_roles_except_new_roles = counter
            # Insert new roles into `role_positions`
            for role in only_new_roles:
                role_positions[role] = counter
                counter += 1
            # Insert old roles into `role_positions`
            for role in all_roles_except_new_roles[pointer_all_roles_except_new_roles:]:
                role_positions[role] = counter
                counter += 1
            # Send new Role-Order to Discord.
            await self.guild.edit_role_positions(positions = role_positions, reason = self.reason)

        return created_roles

    def create_arguments(self, placeholder, element):
        arguments = super().create_arguments(placeholder, element)
        # If `default_colour` is out of range, a random colour will be set
        if self.default_colour > 0xffffff:
            colour = discord.Colour(randint(0x000001, 0xffffff))
        else:
            colour = discord.Colour(self.default_colour)
        # Preparing arguments for `guild.create_role`
        arguments.update({
            'colour': colour,
            'hoist': self.hoist,
            'mentionable': self.mentionable,
        })
        return arguments

    async def guild_create_object(self, *args, **kwargs):
        return await self.guild.create_role(*args, **kwargs)


class CloneChannel(Clone):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_overwrites = {}
        self.roles: Optional[CloneRole] = None
        self.roles_created = {}  # This setting will be set AFTER calling `.create`

    def create_arguments(self, placeholder, element) -> dict:
        arguments = super().create_arguments(placeholder, element)
        overwrites = self.default_overwrites.copy()
        if element in self.roles_created:
            overwrites[self.roles_created[element]] = discord.PermissionOverwrite(read_messages = True,
                                                                                  send_messages = True)
        arguments.update({
            'overwrites': overwrites,
        })
        return arguments

    async def create(self, clone_type: CloneTypeCache):
        if self.roles:
            self.roles_created = await self.roles.create(clone_type)
        await super().create(clone_type)


class CloneDefaultChannel(CloneChannel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category = None

    def create_arguments(self, placeholder, element) -> dict:
        arguments = super().create_arguments(placeholder, element)
        if self.category:
            arguments['category'] = self.category
        return arguments


class CloneVoiceChannel(CloneDefaultChannel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bitrate = 64000  # This is a good default bitrate
        self.user_limit = 0  # Zero means endless

    def create_arguments(self, placeholder, element) -> dict:
        arguments = super().create_arguments(placeholder, element)
        arguments.update({
            'bitrate': self.bitrate,
            'user_limit': self.user_limit,
        })
        return arguments

    async def guild_create_object(self, *args, **kwargs):
        return await self.guild.create_voice_channel(*args, **kwargs)


class CloneTextChannel(CloneDefaultChannel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.slowmode_delay = 0
        self.nsfw = False
        self.topic = ""

    def create_arguments(self, placeholder, element) -> dict:
        arguments = super().create_arguments(placeholder, element)
        arguments.update({
            'slowmode_delay': self.slowmode_delay,
            'nsfw': self.nsfw,
            'topic': self.topic.format(**placeholder),
        })
        return arguments

    async def guild_create_object(self, *args, **kwargs):
        return await self.guild.create_text_channel(*args, **kwargs)


class CloneCategory(CloneChannel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.insert = []  # List With CloneDefaultChannel

    async def guild_create_object(self, *args, **kwargs):
        return await self.guild.create_category(*args, **kwargs)


@commands.command('clone', aliases = ['copy', 'cp'], usage = '(Interactive Menu)')
@commands.has_guild_permissions(manage_channels = True, manage_permissions = True, manage_roles = True)
@commands.bot_has_permissions(embed_links = True, add_reactions = True)
async def clone_toornament(ctx: commands.Context, toornament_id: int, from_choice: int, to_choice: int):
    """Create Channels on Discord that Shadow the Toornament."""
    caching = True
    _ = ctx.bot.translate.get_t_by_ctx(ctx).gettext

    catalog = QuestionCatalog(ctx)
    responses = AwaitResponse(ctx)
    # toornament_id = await catalog.toornament()

    await ctx.send("Please wait while we create a copy of the toornament...")

    if caching and toornament_id in simple_cache:
        tournament = simple_cache[toornament_id]
    else:
        # Get Toornament and cancel Command, if Toornament not found.
        try:
            tournament = await clone_tournament(toornament_id, ctx.bot.viewer_api)
        except ClientResponseError as err:
            if err.status == 404:
                await ctx.send(_("Toornament doesn't exit."))
                raise CancelCommandSilent()
            else:
                raise err
        if caching:
            simple_cache[toornament_id] = tournament

    await ctx.send(embed = create_embed_for_tournament(tournament.tournament))

    # What Options are Possible:
    # Without Binding:
    # Create Voice/Text-Channel (what Category) (+Role)
    # Create Category-Channel (Content) (+Role)
    # Create only Roles
    potential_clone_types = {
        1: CloneTypeParticipants,
        2: CloneTypeParticipantTeam,
        3: CloneTypeStages,
        4: CloneTypeGroups,
        5: CloneTypeRounds,
        6: CloneTypeMatches
    }

    # Make Clone-Settings
    # await ctx.send("1 - Voice, 2 - Text, 3 - Category, 4 - only Roles")
    # choice_to = int(await responses.multiple_choice([str(i) for i in range(1, 5)]))
    potential_clone_settings = {
        1: CloneVoiceChannel,
        2: CloneTextChannel,
        3: CloneCategory,
        4: CloneRole,
    }
    # clone_settings = potential_clone_settings[choice_to]()
    clone_settings = potential_clone_settings[to_choice](ctx.guild)

    if isinstance(clone_settings, CloneChannel):
        clone_settings.roles = CloneRole(ctx.guild)
        clone_settings.roles.name_pattern = '{i} - {name}'
        clone_settings.roles.reason = "Cloning Tournament"
        clone_settings.roles.dry = False
        clone_settings.roles.default_colour = 0x1000000
        clone_settings.roles.position = 7

    # What Data to Fetch
    # await ctx.send(_("What do you want to clone?\n1-Stages\n2-Groups\n3-Rounds\n4-Matches\n5-Participants"))
    # choice_from = int(await responses.multiple_choice([str(i) for i in range(1, 6)]))
    clone_settings.name_pattern = '{i} - {name}'
    clone_settings.dry = False
    clone_settings.reason = "Cloning Tournament"
    clone_settings.topic = 'This is the Channel of {name}'
    clone_settings.category = ctx.channel.category
    clone_type_cache = CloneTypeCache(
        clone_type = potential_clone_types[from_choice],
        tournament_data = tournament,
        filter = lambda element: element.number in ('Weemo', 'nibori'),
        sort_key = lambda element: element.name.lower(),
        sort_reverse = True
    )
    await clone_settings.create(clone_type_cache)

    # @ToDo: Test new CloneTypes


def setup(bot: ToorneyBot):
    bot.add_command(clone_toornament)
