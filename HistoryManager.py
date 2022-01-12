import datetime
import emoji
import time
from operator import itemgetter
from typing import Any, Coroutine

import discord

def getTimeStamp():
    return "[HISTORY] [" + time.strftime('%Y-%m-%d %H:%M:%S') + "]"

# This file has some comments.  Don't get used to it.
class HistoryManager:
    guild: discord.Guild

    def __init__(self, guild, db):
        self.database = db
        self.guild = guild
        self.reactions = []
        self.message_count = 0
        self.reaction_dict = dict({})

    async def analyze_history(self):
        pinned = None
        for channel in self.guild.text_channels:
            try:
                if channel.name == "pins":
                    pinned = await self.get_pinned_messages_time_period(channel, 30)
                else:
                    pass
                    # await self.get_posts_above_reaction_threshold_channel(channel)
            except discord.errors.Forbidden:
                print("[ERROR]", getTimeStamp(), "No access to read " + channel.name)

        for c in self.guild.text_channels:
            try:
                if c.name == "pins":
                    pass
                else:
                    await self.get_posts_above_reaction_threshold_channel(c, pinned)
            except discord.errors.Forbidden:
                print("[ERROR]", getTimeStamp(), "No access to read " + channel.name)

            # If the channel we're reading is server-announcements, save it for later
            if channel.name == "server-announcements":
                server_announcements = channel

        # print("MESSAGE COUNT: ", self.message_count)
        # self.sort_reactions()
        # self.print_reaction_data()
        # # await self.send_reaction_data(server_announcements)
        # self.print_reaction_dictionary()

    async def analyze_channel_history(self, channel: discord.TextChannel):
        message: discord.Message
        one_month_ago = datetime.datetime.now() - datetime.timedelta(days=90)
        for thread in channel.threads:
            await self.get_posts_above_reaction_threshold(thread, "📌", 12, 30)
        async for message in channel.history(limit=None, after=one_month_ago):
            self.message_count += 1
            for reaction in message.reactions:
                self.update_reaction(reaction)
        print(getTimeStamp(), "Successfully analyzed", channel.name)

    def update_reaction(self, react: discord.Reaction):
        if react.is_custom_emoji():
            for reaction in self.reactions:
                if reaction[0] == str(react.emoji):
                    reaction[1] = react.count + reaction[1]
                    return
            self.reactions.append([str(react.emoji), react.count])
            return
        return

    def sort_reactions(self):
        sorted_reactions = sorted(self.reactions, key=itemgetter(1), reverse=True)
        self.reactions = sorted_reactions

    def print_reaction_data(self):
        for reaction in self.reactions:
            print(reaction[0] + "," + str(reaction[1]))

    def print_reaction_dictionary(self):
        for entry in self.reaction_dict.items():
            print("['" + str(entry[0].split(":")[0]) + "', '" + str(entry[0].split(":")[1]) + "', " + str(entry[1]) + "],")

    async def send_reaction_data(self, channel: discord.TextChannel):
        out = "**[Monthly Emoji Usage]**\n"
        for reaction in self.reactions:

            # Parse the reaction's ID out of the string
            id = str(reaction[0].split(">")[0]).split(":")[2]

            # Check if the emoji is still in the server
            for emoji in self.guild.emojis:
                # If the emoji is found, append it to the message
                if str(emoji.id) == str(id):
                    out += reaction[0] + ": " + str(reaction[1]) + "\n"
                    break

        # Send the Monthly Emoji Usage data message to the desired channel
        await channel.send(out)

    async def get_posts_above_reaction_threshold_channel(self, channel: discord.TextChannel, pinned):
        message: discord.Message
        print(channel.name)
        await self.get_posts_above_reaction_threshold(pinned, channel, "📌", 12, 30)
        for thread in channel.threads:
            # print(channel.name, thread.name)
            await self.get_posts_above_reaction_threshold(pinned, thread, "📌", 12, 30)

    async def get_posts_above_reaction_threshold(self, pinned, channel_or_thread, e, thresh, time_in_days):
        message: discord.Message
        one_month_ago = datetime.datetime.now() - datetime.timedelta(days=time_in_days)
        async for message in channel_or_thread.history(limit=None, after=one_month_ago):
            if str(message.id) not in pinned:
                for reaction in message.reactions:
                    if reaction.emoji == e and reaction.count >= thresh:
                        print(str(message.channel.name),str(message.created_at),str(channel_or_thread.id)+","+str(message.id))

    async def get_pinned_messages_time_period(self, channel: discord.TextChannel, days):
        pinned = []
        one_month_ago = datetime.datetime.now() - datetime.timedelta(days=days)
        async for message in channel.history(limit=None, after=one_month_ago):
            link_split = message.content.split("\n")[0].split("/")
            og_message_id = link_split[len(link_split) - 1]
            pinned.append(og_message_id)
        return pinned
