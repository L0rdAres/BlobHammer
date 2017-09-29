# -*- coding: utf-8 -*-
import asyncio
import logging
import time

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
        # help is not very useful as there's only two public commands, it would just disrupt chat
        self.remove_command('help')

        # load the extensions which do the magic
        self.load_extension('bans')
        self.load_extension('roles')

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
        """Sync bans and roles."""
        async with ctx.typing():
            for cog in self.cogs.values():
                sync = getattr(cog, 'sync', None)
                if sync is None:
                    continue

                await sync()
        await ctx.send('Successfully synced bans and roles.')

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
    async def hammer(self, ctx):
        await ctx.send("<:blobhammer:357765371769651201>")

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


bot = BlobHammerBot(command_prefix='!')
bot.run(config.token)
