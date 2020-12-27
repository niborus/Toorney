import logging
import yaml

from config import STATICS
from customFunctions import filehandling

logger = logging.getLogger("discord")


class SafetySettings:

    def __init__(self):
        # initialisiere Variablen
        self.user_blacklist = []
        self.global_mute = True

        print("Import settings: Globalmute / banned user.")
        config = yaml.load(filehandling.read_file(STATICS.SAFETY_CONFIG_FILE))

        # Importiere gebannte User
        if not isinstance(config.get("Ban"), list):
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!!!!!!MAJOR SECURITY ERROR!!!!!!!!!")
            print("!Unable to access blacklisted User.!")
            print("!!!!!!!! RESTART THE BOT !!!!!!!!!!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        else:
            self.user_blacklist = config["Ban"]

        # Importiere die Einstellung für einen globalmute. (Keine Befehle funktionieren, Bot scheint offline)
        if not isinstance(config.get("Globalmute"), bool):
            print("Unable to access the global mute. Global-Mute is set ON")
        else:
            self.global_mute = config["Globalmute"]
            print("Globalmute: {}".format(config["Globalmute"]))

    # Banne User vom Bot
    def global_user_ban(self, discord_id):
        self.user_blacklist.append(discord_id)
        filehandling.edit_yaml(STATICS.SAFETY_CONFIG_FILE, ["Ban"], discord_id, in_a_list = True)

    # Banne User vom Bot
    def global_user_unban(self, discord_id):
        while discord_id in self.user_blacklist:
            self.user_blacklist.remove(discord_id)
        filehandling.edit_yaml(STATICS.SAFETY_CONFIG_FILE, ["Ban"], discord_id, in_a_list = True, adding = False)

    # Schalte den Globalmute an / aus
    def toggle_globale_mute(self, state):  # state  ist entweder True für an oder False für off
        self.global_mute = state
        filehandling.edit_yaml(STATICS.SAFETY_CONFIG_FILE, ["Globalmute"], state)
        logger.info("Set Globalmute: {}".format(state))
