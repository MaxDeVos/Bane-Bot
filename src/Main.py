import logging
import os
import sys
from abc import ABC

from discord.ext import commands
from datetime import datetime

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f'logs/LOG-{datetime.now().strftime("%Y-%m-%d %H_%M_%S")}.log'),
        logging.StreamHandler()
    ]
)

sys.path.insert(1, '')  # if this isn't here, local imports fail in Docker. ¯\_(ツ)_/¯

from src.EmojiRegistration.EmojiRegistrationCog import EmojiRegistrationCog
from src.PinSystem.PinCog import PinCog
from src.TimestampGenerator import TimestampGenerator
from src.Translation.TranslationCog import TranslationCog
from src.WikiCurrentCog.WikiCurrentCog import WikiCurrentCog

ts = TimestampGenerator("BANE")
active_guild_id = int(os.environ.get("GUILD_ID"))

class Bot(commands.Bot, ABC):

    def __init__(self, *args, **kwargs):
        self.guild = None
        self.channelDict = {}
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        # Find guild that matches active_guild_id
        # self.guild = [guild for guild in self.guilds if guild.id == active_guild_id]
        for guild in self.guilds:
            if guild.id == active_guild_id:
                self.guild = guild
                logging.info(f"{ts.get_time_stamp()} Found Guild: {guild.name}")
                break

        # Populate channelDict for future convenience
        for a in self.guild.text_channels:
            self.channelDict[a.name] = a

        # Start cogs
        logging.info(f"{ts.get_time_stamp()} Starting Cogs")
        self.add_cog(PinCog(bot, self))
        self.add_cog(TranslationCog(bot))
        # self.add_cog(EmojiRegistrationCog(bot, self))
        # self.add_cog(WikiCurrentCog(bot, self))

        # Send Message
        # ch = await self.fetch_channel(852322660125114398)
        # await ch.send("I'm back, asswipes")

        # Add reaction
        # ch = await self.fetch_channel(852322660125114398)
        # msg = await ch.fetch_message(959300803972190259)
        # await msg.add_reaction("🟠")


# Create and start Bane Bot
bot = Bot()
bot.run(os.environ.get('APIKEY'))
