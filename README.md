# Toorney

This is a Open-Source Public Discord Bot, that can connect Toornament.com with Discord.

## Using the Public Version:

You can invite the Public Bot with one of the following links:

- [Admin](https://discord.com/api/oauth2/authorize?client_id=792863663609348106&permissions=8&scope=bot%20applications.commands)
This isn't a recommended option, but it's a option.
- [Nearly all permissions](https://discord.com/api/oauth2/authorize?client_id=792863663609348106&permissions=2147483633&scope=bot%20applications.commands)
This is useful if you want to be sure every future update is working correctly, without renew permissions.
- [Recommended](https://discord.com/api/oauth2/authorize?client_id=792863663609348106&permissions=490204272&scope=bot%20applications.commands)
My favorite. Not too much, not too less.
- [Minimalistic](https://discord.com/api/oauth2/authorize?client_id=792863663609348106&permissions=379968&scope=bot%20applications.commands)
At least you can interact with the Bot.

All the Links above include the `applications.commands`-Permission, which enables slash commands.
(We don't have slash-commands yet)

If you don't want to add `applications.commands`-Permission, use one of the following links:

- [Admin](https://discord.com/api/oauth2/authorize?client_id=792863663609348106&permissions=8&scope=bot),
[Nearly all permissions](https://discord.com/api/oauth2/authorize?client_id=792863663609348106&permissions=2147483633&scope=bot),
[Recommended](https://discord.com/api/oauth2/authorize?client_id=792863663609348106&permissions=490204272&scope=bot),
[Minimalistic](https://discord.com/api/oauth2/authorize?client_id=792863663609348106&permissions=379968&scope=bot)

## For Developer:

### Refresh Translations
1. Generate a pot-File: `pygettext -d locale/pots/guess .`
1. Merge all Pot-Files: `msgcat locale/pots/*.pot > locale/base.pot`
1. Merge Pot-Files to Po-Files: `msgmerge -U locale/{lang}/LC_MESSAGES/interface.po locale/base.pot`
