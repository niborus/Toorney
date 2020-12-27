import git, sys
from config import STATICS


def console_start(discord_version, server_number):
    repo = git.Repo(search_parent_directories = True)
    branch = repo.active_branch
    print("Bot is running")
    header = """
  __  __       ____        _                 _   
 |  \/  |     |  _ \      | |     /\        | |  
 | \  / |_   _| |_) | ___ | |_   /  \   _ __| |_ 
 | |\/| | | | |  _ < / _ \| __| / /\ \ | '__| __|
 | |  | | |_| | |_) | (_) | |_ / ____ \| |  | |_ 
 |_|  |_|\__, |____/ \___/ \__/_/    \_\_|   \__|
          __/ |                                  
         |___/                                   
    """
    print(header)
    print(STATICS.BOT_NAME)
    print("\n\n Branch: %s     Version: %s" % (branch.name, STATICS.BOT_VERSION))
    print("\n Python: %s\n\n Discord: %s" % (sys.version.split("\n")[0], discord_version))
    print("\n Running on %i Server(n)\n\n" % server_number)
