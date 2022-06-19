from abc import ABCMeta
from contextlib import suppress

import discord
from redbot.core import commands

from .abc import MixinMeta
from .falxclass import Allowance


class Listeners(MixinMeta, metaclass=ABCMeta):
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        if not self.is_enabled:
            return
        if await self.should_leave_guild(guild):
            if guild.owner:
                with suppress(discord.HTTPException):
                    await guild.owner.send(await self.get_leaving_message())
            await guild.leave()
        allowance = await Allowance.from_guild(guild, self.config)
        embed = self.generate_join_embed_for_guild(guild, is_accepted=allowance.is_allowed)
        if channel := await self.get_notification_channel():
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        if not self.is_enabled:
            return
        if await self.config.autoremove():
            guild_info = await Allowance.from_guild(guild, self.config)
            if not guild_info.is_allowed:
                return
            await guild_info.disallow_guild(self.bot.user, "Automatic Removal")
        embed = await self.generate_leave_embed_for_guild(guild)
        if channel := await self.get_notification_channel():
            await channel.send(embed=embed)
