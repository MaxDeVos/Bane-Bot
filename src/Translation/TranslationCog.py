import logging

from discord.ext import commands
from googletrans import Translator
import discord
import re
from difflib import SequenceMatcher

from src.TimestampGenerator import TimestampGenerator

log = logging.getLogger(__name__)
translator = Translator()
ts = TimestampGenerator("LANG")


class TranslationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        log.info(f"{ts.get_time_stamp()} Successfully Started Translation Engine")

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            await handle_translation(message)


async def handle_translation(message):
    try:

        content = cleanse_emojis(message)

        lang = translator.detect(content)

        log.info(f"language: {lang.lang} @ {lang.confidence} |  message: {content} ")

        if lang.lang == "es" or lang.lang == "de" or lang.lang == "iw":

            if determinePermissions(message, lang.lang):
                log.info(f"{ts.get_time_stamp()} {message.author.name} to {lang.lang} : {content}")
                translation = translator.translate(content).text

                similarity_index = similar(str(translation).lower(), str(content.lower()))

                # Check if translation is the same
                if str(translation).lower().replace(" ", "") != content and \
                        str(translation).lower() != content and similarity_index < 0.95:
                    emojied_translation = replenesh_emojis(message, translation)
                    await message.reply("**Translation:  **" + str(emojied_translation).replace("things", "stuff"),
                                        mention_author=False)
            else:
                log.info(f"{ts.get_time_stamp()} Denied {message.author.name} translation to {lang.lang}")
    except TypeError:
        return
    except Exception as e:
        log.error(f"{ts.get_time_stamp()} {str(e)}")


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def cleanse_emojis(message: discord.Message):
    out: str
    out = message.content
    for match in re.findall("(?<=<)(.*?)(?=>)", out):
        out = out.replace(match, re.findall("(?:[^:]*:s*){2}(.*)", match)[0])
    return out


def replenesh_emojis(message: discord.Message, content):
    guild: discord.Guild
    guild = message.guild

    log.info(content)
    i = 0
    for match in re.findall("(?<=<)(.*?)(?=>)", content):
        match = "<" + match + ">"
        i+=1
        emoji: discord.Emoji
        for emoji in guild.emojis:
            if emoji.id == int(match.replace("<", "").replace(">", "")):
                content = content.replace(match, str(emoji), 1)

    return content


def determinePermissions(message, language):
    if language == "es":
        role_name = "Spanish Speakers"
    elif language == "de":
        role_name = "German Speakers"
    elif language == "iw":
        role_name = "Hebrew Speakers"
    else:
        return False

    for r in message.author.roles:
        if r.name == role_name:
            return True
    return False
