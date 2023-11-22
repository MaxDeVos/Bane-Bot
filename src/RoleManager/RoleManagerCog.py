import logging

log = logging.getLogger(__name__)

import discord
from discord.ext import commands

from src.TimestampGenerator import TimestampGenerator

ts = TimestampGenerator("ROLE")

class RoleManagerCog(commands.Cog):
    guild: discord.Guild

    def __init__(self, bot, parent):
        self.bot = bot
        self.parent = parent
        log.info(f"{ts.get_time_stamp()} Starting Role Manager")
