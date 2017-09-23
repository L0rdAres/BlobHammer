# -*- coding: utf-8 -*-
import discord
from discord.ext import commands

from config import BLOB_GUILD, ROLES


class Roles:
    """Cog to sync roles across multiple guilds."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def on_member_join(self, member: discord.Member):
        blob_guild = self.bot.get_guild(BLOB_GUILD)
        blob_member = blob_guild.get_member(member.id)
        if blob_member is None:
            return  # no roles can be synced if they aren't in the main guild

        for blob_role in blob_member.roles:
            if blob_role.id not in ROLES.keys():
                continue

            role_id = ROLES[blob_role.id][member.guild.id]
            role = discord.utils.get(member.guild.roles, id=role_id)
            await member.add_roles(role)

    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.guild.id != BLOB_GUILD:
            return

        if before.roles == after.roles:
            return

        old = set(before.roles)
        new = set(after.roles)

        for role in old.symmetric_difference(new):
            if role.id not in ROLES.keys():
                continue

            to_sync = ROLES.get(role.id)
            for guild_id, role_id in to_sync.items():
                guild = self.bot.get_guild(guild_id)

                # the user may not be in all synced guilds
                member = guild.get_member(before.id)
                if member is None:
                    continue

                guild_role = discord.utils.get(guild.roles, id=role_id)

                if role in old:
                    await member.remove_roles(guild_role)
                else:
                    await member.add_roles(guild_role)

    async def sync(self):
        """Syncs all roles from the main guild."""
        blob_guild = self.bot.get_guild(BLOB_GUILD)

        for blob_role_id in ROLES:
            blob_role = discord.utils.get(blob_guild.roles, id=blob_role_id)

            blob_members = set(x.id for x in blob_role.members)
            print(blob_members)

            # guild_id: role_id pair of guilds which have this role to sync to
            for guild_id, role_id in ROLES[blob_role_id].items():
                guild = self.bot.get_guild(guild_id)
                role = discord.utils.get(guild.roles, id=role_id)
                print(guild, role)

                members = set(x.id for x in role.members)
                diff = blob_members.symmetric_difference(members)

                for user_id in diff:
                    member = guild.get_member(user_id)
                    if member is None:
                        continue

                    if user_id in blob_members:
                        await member.add_roles(role, reason='sync - user has role in main guild')
                    else:
                        await member.remove_roles(role, reason='sync - user no longer has role in main guild')

    @commands.command()
    @commands.is_owner()
    async def roles(self, ctx: commands.Context, guild_id: int):
        """shows all role ids for a guild."""
        guild = self.bot.get_guild(guild_id)
        if guild is None:
            return await ctx.send('Can\'t find guild, please try again!')

        roles = []
        for role in guild.role_hierarchy:
            roles.append(f'{role.id} - {role.name}')

        result = '\n'.join(roles)
        await ctx.send(f'```\n{result}```')


def setup(bot: commands.Bot):
    bot.add_cog(Roles(bot))
