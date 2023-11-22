import logging

import discord
from discord.ext import commands

from src.PinSystem.PinHandler import PinHandler
from src.TimestampGenerator import TimestampGenerator

log = logging.getLogger(__name__)
ts = TimestampGenerator("PINS")

class PinCog(commands.Cog):
    guild: discord.Guild

    def __init__(self, bot, parent):
        self.bot = bot
        self.parent = parent
        self.pinHandler = None
        log.info(f"{ts.get_time_stamp()} Starting Pin Manager")
        self.pinHandler = PinHandler(self.parent.channelDict["pins"], self.parent.guild)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction: discord.RawReactionActionEvent):
        if reaction.guild_id == self.parent.guild.id:
            await self.pinHandler.handlePinReaction(reaction, self.parent)
