# -*- coding: utf-8 -*-
import asyncio
import datetime
import logging
import time
from typing import Union

import discord
from discord.ext import commands

import config


IGNORED_ERRORS = (
    commands.CommandNotFound,
    commands.CheckFailure,
    commands.NoPrivateMessage,
    commands.NotOwner,
    commands.DisabledCommand,
)


logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='hammer.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


class BlobHammerBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.extra_guilds = []
        self.add_command(self.sync)
        self.add_command(self.ping)
        self.add_command(self.update)
        self.add_command(self.restart)
        # help is not very useful as there's only two commands, it would just disrupt chat
        self.remove_command('help')

    async def on_ready(self):
        self.extra_guilds = [self.get_guild(x) for x in config.EXTRA_GUILDS]

    async def on_member_ban(self, guild: discord.Guild, user: Union[discord.Member, discord.User]):
        if guild.id != config.BLOB_GUILD:
            return

        reason = await self.get_reason(guild, discord.AuditLogAction.ban, user)

        for guild in self.extra_guilds:
            await guild.ban(user, reason=reason)

        mod_log = self.get_channel(config.MOD_LOG)
        await mod_log.send(f'{config.BLOB_HAMMER} {user} (`{user.id}`) cross banned.')

    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        if guild.id != config.BLOB_GUILD:
            return

        reason = await self.get_reason(guild, discord.AuditLogAction.unban, user)

        for guild in self.extra_guilds:
            await guild.unban(user, reason=reason)

        mod_log = self.get_channel(config.MOD_LOG)
        await mod_log.send(f'{config.BOLB} {user} (`{user.id}`) cross unbanned.')

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, IGNORED_ERRORS):
            return

        # get the actual error if something weird happened in a command
        if isinstance(error, commands.CommandInvokeError):
            error = error.original

        logger.exception(f'unexpected error while running the {ctx.command} command', exc_info=error)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def sync(self, ctx: commands.Context):
        """Sync bans."""
        async with ctx.typing():
            blob_guild = self.get_guild(config.BLOB_GUILD)
            blob_bans = set(x.user for x in await blob_guild.bans())

            for guild in self.extra_guilds:
                bans = set(x.user for x in await guild.bans())
                diff = blob_bans.symmetric_difference(bans)

                for ban in diff:
                    if ban in bans:
                        await guild.unban(ban, reason='sync - user not banned on main guild')
                    else:
                        await guild.ban(ban, reason='sync - user banned on main guild')

        await ctx.send('Successfully synced bans.')

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ping(self, ctx: commands.Context):
        """Pong!"""
        before = time.perf_counter()
        msg = await ctx.send('Pon..')
        after = time.perf_counter()

        ws = self.latency * 1000
        rtt = (after - before) * 1000

        await msg.edit(content=f'Pong! rtt {rtt:.3f}ms, ws: {ws:.3f}ms')

    @commands.command()
    @commands.is_owner()
    async def update(self, ctx: commands.Context):
        """Update from git."""
        async with ctx.typing():
            process = await asyncio.create_subprocess_shell(
                'git pull', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            results = await process.communicate()
            result = ''.join(x.decode('utf-8') for x in results)
        await ctx.send(f'```{result}```')

    @commands.command()
    @commands.is_owner()
    async def restart(self, ctx: commands.Context):
        await ctx.send('ok')
        await self.logout()

    async def get_reason(self, guild: discord.Guild, action: discord.AuditLogAction, target) -> str:
        """Get the reason an action was performed on something."""
        # since the audit log is slow sometimes
        await asyncio.sleep(4)

        before_sleep = datetime.datetime.utcnow() - datetime.timedelta(seconds=15)
        async for entry in guild.audit_logs(limit=20, after=before_sleep, action=action):
            if entry.target != target:
                continue

            return entry.reason if entry.reason is not None else 'no reason specified'
        return 'no reason found'


bot = BlobHammerBot(command_prefix='!')
bot.run(config.token)
