import discord
from aiohttp import ClientResponseError
from discord.ext import commands
from ToorneyBot import ToorneyBot
from interactive_menu import QuestionCatalog, AwaitResponse
from CustomErrors import CancelCommandSilent
from customFunctions.diverse import create_embed_for_tournament
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
                        range=toornament.Range(i*max_range, (i+1)*max_range - 1)
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
    def __init__(self):
        pass

    def get_placeholder_from_element(self, element, tournament_data: TournamentData):
        """Takes a Element (like Player, Toornament, ) and the Data of the Tournament and creates a dict
        for placeholders."""
        return {
            'id': element.id
        }

    def get_elements(self, tournament_data: TournamentData):
        """:returns All Elements"""
        return []


class CloneTypeStages(CloneType):
    def __init__(self):
        super().__init__()


class CloneTypeGroups(CloneType):
    def __init__(self):
        super().__init__()


class CloneTypeRounds(CloneType):
    def __init__(self):
        super().__init__()


class CloneTypeMatches(CloneType):
    def __init__(self):
        super().__init__()


class CloneTypeTeamParticipants(CloneType):
    def __init__(self):
        super().__init__()


class CloneTypeParticipants(CloneType):
    def __init__(self):
        super().__init__()

    def get_placeholder_from_element(self, participant: toornament.ParticipantPlayer, tournament_data: TournamentData):
        placeholder = super().get_placeholder_from_element(participant, tournament_data)
        placeholder.update({
            'name': participant.name
        })
        return placeholder

    def get_elements(self, tournament_data: TournamentData):
        return tournament_data.participants.values()


class CloneTypeIndividualParticipants(CloneTypeParticipants):
    def __init__(self):
        super().__init__()


class CloneTypeSingleParticipants(CloneTypeParticipants):
    def __init__(self):
        super().__init__()


class Clone:
    def __init__(self):
        self.create_type = None
        self.name_pattern = "{i}"

    async def create(self, clone_type: CloneType, tournament_data: TournamentData):
        """Clones the Toornament to the server. Setting must be given before"""


class CloneRole(Clone):
    def __init__(self):
        super().__init__()
        self.default_colour = None
        self.mentionable = False
        self.hoist = False
        self.position = None

    async def create(self, clone_type: CloneType, tournament_data: TournamentData):
        elements = clone_type.get_elements(tournament_data)
        i = 1
        for element in elements:
            placeholder = {'i': i}
            placeholder.update(clone_type.get_placeholder_from_element(element, tournament_data))
            role_name = self.name_pattern.format(**placeholder)
            print("Create Role: {name}".format(name = role_name))
            i += 1


class CloneChannel(Clone):
    def __init__(self):
        super().__init__()
        self.default_overwrites = None


class CloneDefaultChannel(CloneChannel):
    def __init__(self):
        super().__init__()
        self.category = None
        self.topic = ""


class CloneVoiceChannel(CloneDefaultChannel):
    def __init__(self):
        super().__init__()
        self.bitrate = None
        self.user_limit = None


class CloneTextChannel(CloneDefaultChannel):
    def __init__(self):
        super().__init__()


class CloneCategory(CloneChannel):
    def __init__(self):
        super().__init__()
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
    clone_settings = potential_clone_settings[4]()

    # What Data to Fetch
    # await ctx.send(_("What do you want to clone?\n1-Stages\n2-Groups\n3-Rounds\n4-Matches\n5-Participants"))
    # choice_from = int(await responses.multiple_choice([str(i) for i in range(1, 6)]))
    clone_settings.name_pattern = '{i} - {name}'
    clone_type = CloneTypeSingleParticipants()
    await clone_settings.create(clone_type, tournament_data = tournament)


def setup(bot: ToorneyBot):
    bot.add_command(clone_toornament)
