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

    def create_arguments(self, placeholder) -> dict:
        """Creates the arguments needed for the `create_OBJETC` Method."""
        return {
            'name': self.name_pattern.format(**placeholder),
            'reason': self.reason
        }

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
            # This fetches the roles from Discord and sends a fully ordered list with role-positions back.
            # The internal cache has huge problems to keep track of role positions.
            # Remember the IDs of the Roles created
            created_roles_ids = [role.id for role in created_roles]
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

    def create_arguments(self, placeholder):
        arguments = super().create_arguments(placeholder)
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

    async def create_single(self, placeholder):
        arguments = self.create_arguments(placeholder)
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

    def create_arguments(self, placeholder) -> dict:
        arguments = super().create_arguments(placeholder)
        arguments.update({
            'overwrites': self.default_overwrites,
        })
        return arguments


class CloneDefaultChannel(CloneChannel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category = None

    def create_arguments(self, placeholder) -> dict:
        arguments = super().create_arguments(placeholder)
        if self.category:
            arguments['category'] = self.category
        return arguments


class CloneVoiceChannel(CloneDefaultChannel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bitrate = 64000  # This is a good default bitrate
        self.user_limit = 0  # Zero means endless

    def create_arguments(self, placeholder) -> dict:
        arguments = super().create_arguments(placeholder)
        arguments.update({
            'bitrate': self.bitrate,
            'user_limit': self.user_limit,
        })
        return arguments

    async def create_single(self, placeholder):
        arguments = self.create_arguments(placeholder)
        if not self.dry:
            await sleep(1.0)
            new_channel = await self.guild.create_voice_channel(**arguments)
            return new_channel
        else:
            print_arguments(**arguments)


class CloneTextChannel(CloneDefaultChannel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.slowmode_delay = 0
        self.nsfw = False
        self.topic = ""

    def create_arguments(self, placeholder) -> dict:
        arguments = super().create_arguments(placeholder)
        arguments.update({
            'slowmode_delay': self.slowmode_delay,
            'nsfw': self.nsfw,
            'topic': self.topic.format(**placeholder),
        })
        return arguments

    async def create_single(self, placeholder):
        arguments = self.create_arguments(placeholder)
        if not self.dry:
            await sleep(1.0)
            new_channel = await self.guild.create_text_channel(**arguments)
            return new_channel
        else:
            print_arguments(**arguments)


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
        2: CloneTextChannel,
        3: CloneCategory,
        4: CloneRole,
    }
    # clone_settings = potential_clone_settings[choice_to]()
    clone_settings = potential_clone_settings[1](ctx.guild)

    # What Data to Fetch
    # await ctx.send(_("What do you want to clone?\n1-Stages\n2-Groups\n3-Rounds\n4-Matches\n5-Participants"))
    # choice_from = int(await responses.multiple_choice([str(i) for i in range(1, 6)]))
    clone_settings.name_pattern = '{i} - {name}'
    clone_settings.dry = True
    clone_settings.reason = "Cloning Tournament"
    clone_settings.topic = 'This is the Channel of {name}'
    clone_settings.category = ctx.channel.category
    clone_type = CloneTypeSingleParticipants(tournament)
    await clone_settings.create(clone_type)


def setup(bot: ToorneyBot):
    bot.add_command(clone_toornament)
