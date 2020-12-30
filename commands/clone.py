import discord
from asyncio import sleep
from aiohttp import ClientResponseError
from discord.ext import commands
from random import randint
from ToorneyBot import ToorneyBot
from interactive_menu import QuestionCatalog, AwaitResponse
from CustomErrors import CancelCommandSilent
from customFunctions.diverse import create_embed_for_tournament, print_arguments
import toornament


class TournamentData:
    def __init__(self, tournament: toornament.TournamentDetailed, stages: dict, groups: dict,
                 rounds: dict, matches: dict, participants: dict):
        self.tournament = tournament
        self.stages = stages
        self.groups = groups
        self.rounds = rounds
        self.matches = matches
        self.participants = participants


async def clone_tournament(tournament_id, api: toornament.AsyncViewerAPI):
    tournament_data = {
        'tournament': await api.get_tournament(tournament_id),
        'stages': {stage.id: stage for stage in await api.get_stages(tournament_id)},
        'groups': {},
        'rounds': {},
        'matches': {},
        'participants': {},
    }

    async def get_all(element, max_range, api_function):
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
    def __init__(self, tournament_data: TournamentData):
        self.tournament_data = tournament_data

    def get_placeholder_from_element(self, element):
        """Takes a Element (like Player, Toornament, ) and the Data of the Tournament and creates a dict
        for placeholders."""
        return {
            'id': element.id
        }

    def get_elements(self):
        """:returns All Elements"""
        return []


class CloneTypeStages(CloneType):
    pass


class CloneTypeGroups(CloneType):
    pass


class CloneTypeRounds(CloneType):
    pass


class CloneTypeMatches(CloneType):
    pass


class CloneTypeTeamParticipants(CloneType):
    pass


class CloneTypeParticipants(CloneType):

    def get_placeholder_from_element(self, participant: toornament.ParticipantPlayer):
        placeholder = super().get_placeholder_from_element(participant)
        placeholder.update({
            'name': participant.name
        })
        return placeholder

    def get_elements(self):
        return self.tournament_data.participants.values()


class CloneTypeIndividualParticipants(CloneTypeParticipants):
    pass


class CloneTypeSingleParticipants(CloneTypeParticipants):
    pass


class Clone:
    def __init__(self, guild: discord.Guild):
        self.dry = False
        self.reason = None
        self.guild = guild
        self.create_type = None
        self.name_pattern = "{i}"

    async def create(self, clone_type: CloneType):
        """Clones the Toornament to the server. Setting must be given before"""
        elements = clone_type.get_elements()
        i = 1
        created_objects = []
        for element in elements:
            placeholder = {'i': i}
            placeholder.update(clone_type.get_placeholder_from_element(element))
            created_objects.append(await self.create_single(placeholder))
            i += 1
        return created_objects

    async def create_single(self, placeholder):
        """Creates a Single Instance, like one Role or one Channel"""


class CloneRole(Clone):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_colour = 0
        self.mentionable = False
        self.hoist = False
        self.position = 1

    async def create(self, clone_type: CloneType):
        created_roles = await super().create(clone_type)
        if not self.dry and created_roles:
            created_roles_ids = [role.id for role in created_roles]
            all_roles = await self.guild.fetch_roles()
            all_roles.sort(key = lambda r: r.position)
            all_roles_except_new_roles = [role for role in all_roles if role.id not in created_roles_ids]
            only_new_roles = [role for role in all_roles if role.id in created_roles_ids]
            role_positions = {}
            counter = 0
            for role in all_roles_except_new_roles[:self.position]:
                role_positions[role] = counter
                counter += 1
            pointer_all_roles_except_new_roles = counter
            for role in only_new_roles:
                role_positions[role] = counter
                counter += 1
            for role in all_roles_except_new_roles[pointer_all_roles_except_new_roles:]:
                role_positions[role] = counter
                counter += 1
            await self.guild.edit_role_positions(positions = role_positions, reason = self.reason)

        return created_roles

    async def create_single(self, placeholder):
        role_name = self.name_pattern.format(**placeholder)
        print("Create Role: {name}".format(name = role_name))
        if self.default_colour > 0xffffff:
            colour = discord.Colour(randint(0x000001, 0xffffff))
        else:
            colour = discord.Colour(self.default_colour)
        arguments = {
            'name': role_name,
            'colour': colour,
            'hoist': self.hoist,
            'mentionable': self.mentionable,
            'reason': self.reason,
        }
        if not self.dry:
            await sleep(1.0)
            new_role = await self.guild.create_role(**arguments)
            return new_role
        else:
            print_arguments(**arguments)


class CloneChannel(Clone):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_overwrites = None


class CloneDefaultChannel(CloneChannel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category = None
        self.topic = ""


class CloneVoiceChannel(CloneDefaultChannel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bitrate = None
        self.user_limit = None


class CloneTextChannel(CloneDefaultChannel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class CloneCategory(CloneChannel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.insert = []  # List With CloneDefaultChannel


@commands.command('clone', aliases = ['copy', 'cp'], usage = '(Interactive Menu)')
@commands.has_guild_permissions(manage_channels = True, manage_permissions = True, manage_roles = True)
@commands.bot_has_permissions(embed_links = True, add_reactions = True)
async def clone_toornament(ctx: commands.Context):
    """Create Channels on Discord that Shadow the Toornament."""
    _ = ctx.bot.translate.get_t_by_ctx(ctx).gettext

    catalog = QuestionCatalog(ctx)
    responses = AwaitResponse(ctx)
    toornament_id = await catalog.toornament()

    await ctx.send("Please wait while we create a copy of the toornament...")

    # Get Toornament and cancel Command, if Toornament not found.
    try:
        tournament = await clone_tournament(toornament_id, ctx.bot.viewer_api)
    except ClientResponseError as err:
        if err.status == 404:
            await ctx.send(_("Toornament doesn't exit."))
            raise CancelCommandSilent()
        else:
            raise err

    await ctx.send(embed = create_embed_for_tournament(tournament.tournament))

    # What Options are Possible:
    # Without Binding:
    # Create Voice/Text-Channel (what Category) (+Role)
    # Create Category-Channel (Content) (+Role)
    # Create only Roles

    # Make Clone-Settings
    # await ctx.send("1 - Voice, 2 - Text, 3 - Category, 4 - only Roles")
    # choice_to = int(await responses.multiple_choice([str(i) for i in range(1, 5)]))
    potential_clone_settings = {
        1: CloneVoiceChannel,
        2: CloneDefaultChannel,
        3: CloneCategory,
        4: CloneRole,
    }
    # clone_settings = potential_clone_settings[choice_to]()
    clone_settings = potential_clone_settings[4](ctx.guild)

    # What Data to Fetch
    # await ctx.send(_("What do you want to clone?\n1-Stages\n2-Groups\n3-Rounds\n4-Matches\n5-Participants"))
    # choice_from = int(await responses.multiple_choice([str(i) for i in range(1, 6)]))
    clone_settings.name_pattern = '{i} - {name}'
    clone_settings.dry = False
    clone_settings.reason = "Cloning Tournament"
    clone_settings.default_colour = 0xee5577
    clone_settings.position = 5
    clone_type = CloneTypeSingleParticipants(tournament)
    await clone_settings.create(clone_type)


def setup(bot: ToorneyBot):
    bot.add_command(clone_toornament)
