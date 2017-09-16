# BlobHammer

[![python](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/)
[![license](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/FrostLuma/Mousey/blob/master/LICENSE)

Simple discord bot to sync bans across guilds

# Usage

Due to BlobHammer being a private bot meant for use on specified guilds
it's not configurable within discord and can not be invited.

To run your own instance edit the `MOD_LOG`, `BLOB_GUILD`,
`EXTRA_GUILDS` ids in `run.py` and exchange the emoji used for emoji
your bot can use.

The bot requires the `ban members` permission in every active guild
and the `view audit log` permission in the main guild, which
'dispatches' the bans to the others.
