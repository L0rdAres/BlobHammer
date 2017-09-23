# BlobHammer

[![python](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/)
[![license](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/FrostLuma/Mousey/blob/master/LICENSE)

Simple discord bot to sync bans across guilds

# Usage

Due to BlobHammer being a private bot meant for use on specified guilds
it's not configurable within discord and can not be invited.

To run your own instance simply copy the example config and save it
with your edits as `config.py`.

The bot requires the `ban members` and `manage roles` permission in
every active guild and the `view audit log` permission in the main
guild, which 'dispatches' the bans and role edits to the others.
