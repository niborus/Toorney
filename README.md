# Supporter

## Geplanter Funktionsumfang
Siehe [Issues](https://github.com/niborus/Friendly-Bot/labels/enhancement)

## Übersetzung aktualisieren
1. Generieren der pot-Datei: `pygettext -d locale/pots/guess .`
1. Alle pot-Dateien zusammenführen: `msgcat locale/pots/*.pot > locale/base.pot`
1. pot-Datei in po mergen: `msgmerge -U locale/{lang}/LC_MESSAGES/interface.po locale/base.pot`

## Aufbau eines Command-Help-Text

### Description

Dies sollte die eigentliche Beschreibung des Befehls sein. Was macht er, was braucht er?
Nachricht wird im Hilfsbefehl des Commands ganz oben angezeigt.

### Brief

Kurzer Hilfstext für den Befehl. (Für einzelne Zeile)

### Help

Langer Hilfstext für den Befehl.

### short_doc

Eine Kurz-Dokumentation des Befehls. **Nicht manuell vergeben!**
Es ist `brief` oder Zeile 1 von `help`.
