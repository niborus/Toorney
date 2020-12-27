import os, yaml, collections.abc, typing
from typing import Tuple, Set, Any
from customFunctions import filehandling, diverse


def deep_list_to_set(d):
    for k, v in d.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = deep_list_to_set(d.get(k, {}))
        elif isinstance(v, list):
            d[k] = set(v)
    return d


def load_extensions():
    """:return a dict with the extension and an boolean if they can be loaded
    extensions has extension_name :key and loadable as value (boolean)"""

    extensions_places = {
        "Whitelist": {
            "Folders": [],
            "Files": [],
            "Unloaded": []
        },
        "Blacklist": {
            "Folders": [],
            "Files": [],
            "Unloaded": []
        }
    }
    extensions = {}

    # Load the Dict from extensions.yml
    # This will raise an error if the file does not exist.
    content = yaml.load(filehandling.read_file("config/extensions.yml"))
    if content is not None:
        extensions_places = diverse.deep_update(extensions_places, content)

    # Load the Dict from extensions.local.yml, if file exists
    if os.path.isfile("config/extensions.local.yml"):
        content = yaml.load(filehandling.read_file("config/extensions.local.yml"))
        if content is not None:
            extensions_places = diverse.deep_update(extensions_places, content)

    # Converting the list to sets.
    extensions_places = deep_list_to_set(extensions_places)

    # Removing Blacklisted Items from the Whitelist.
    for path in {"Folders", "Files", "Unloaded"}:
        for k in extensions_places["Blacklist"][path]:
            extensions_places["Whitelist"][path].discard(k)

    # get extensions from Folders:
    for folder in extensions_places["Whitelist"]["Folders"]:
        for file in os.listdir("./%s" % folder.replace('.', '/')):
            if file.endswith(".py") and not file.startswith("_"):
                if '.' not in file[:-3]:  # Separate line so it won't raise an error if len(file)<3
                    extensions["{}.{}".format(folder, file[:-3])] = True

    # get extensions from YML-List:
    for e in extensions_places["Whitelist"]["Files"]:
        extensions[e] = True

    # Remove Blacklisted Extensions:
    for e in extensions_places["Blacklist"]["Files"]:
        if e in extensions:
            extensions.pop(e)

    # Make Unloaded Items False:
    for e in extensions_places["Whitelist"]["Unloaded"]:
        if e in extensions:
            extensions[e] = False

    return extensions


def loadable():
    """:return a set with Extensions that can be loaded """
    extensions: Set[str] = set()
    for k, v in load_extensions().items():
        if v:
            extensions.add(k)
    return extensions


def unloadable():
    """:return a set with Extensions that can not or should not be loaded """
    extensions: Set[str] = set()
    for k, v in load_extensions().items():
        if not v:
            extensions.add(k)
    return extensions


def all_extensions():
    """:return a set with Extensions all extensions"""
    return set(load_extensions().keys())


def add_to_unloaded(extension: str):
    filehandling.edit_yaml("config/extensions.local.yml",
                           ["Whitelist", "Unloaded"],
                           extension,
                           adding=True,
                           in_a_list=True)


def remove_from_unloaded(extension: str):
    filehandling.edit_yaml("config/extensions.local.yml",
                           ["Whitelist", "Unloaded"],
                           extension,
                           adding=False,
                           in_a_list=True)
