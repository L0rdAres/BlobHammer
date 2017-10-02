# -*- coding: utf-8 -*-
import datetime

import discord
from discord.ext import commands

from config import MINI_MOD_LOGS, NO, YES


SECOND = 1
MINUTE = SECOND * 60
HOUR = MINUTE * 60
DAY = HOUR * 24
WEEK = DAY * 7
MONTH = DAY * 30
YEAR = DAY * 365


def human_delta(delta):
    delta = int(delta)

    if delta <= 0:
        return "0s"

    years, rest = divmod(delta, YEAR)
    months, rest = divmod(rest, MONTH)
    days, rest = divmod(rest, DAY)
    hours, rest = divmod(rest, HOUR)
    minutes, seconds = divmod(rest, MINUTE)

    periods = [("y", years), ("mo", months), ("d", days), ("h", hours), ("m", minutes), ("s", seconds)]
    periods = [f"{value}{name}" for name, value in periods if value > 0]

    if len(periods) > 2:
        return f'{periods[0]}, {periods[1]} and {periods[2]}'
    return " and ".join(periods)


class Logs:
    """Simple mod logs to monitor joins and leaves."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def on_member_join(self, member: discord.Member):
        channel_id = MINI_MOD_LOGS.get(member.guild.id)
        if channel_id is None:
            return

        channel = self.bot.get_channel(channel_id)

        now = datetime.datetime.utcnow()
        delta = (now - member.created_at).total_seconds()

        create_delta = human_delta(delta)
        is_new = ' \N{SQUARED NEW}' if delta < 60 * 60 else ''

        msg = f'{YES} `{member} {member.id}` joined (created `{create_delta}` ago{is_new}) {member.mention}'
        await channel.send(msg)

    async def on_member_remove(self, member: discord.Member):
        channel_id = MINI_MOD_LOGS.get(member.guild.id)
        if channel_id is None:
            return

        channel = self.bot.get_channel(channel_id)

        now = datetime.datetime.utcnow()
        delta = (now - member.created_at).total_seconds()

        join_delta = human_delta(delta)

        if len(member.roles) > 1:
            roles = ', '.join((x.name for x in member.roles if not x.is_default()))
            roles = f'; roles: `{roles}`'
        else:
            roles = ''

        msg = f'{NO} `{member} {member.id}` left (joined `{join_delta}` ago{roles}) {member.mention}'
        await channel.send(msg)


def setup(bot: commands.Bot):
    bot.add_cog(Logs(bot))
