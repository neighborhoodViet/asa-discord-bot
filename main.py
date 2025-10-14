import discord
from discord.ext import commands, tasks
import logging
from dotenv import load_dotenv
import os
import json
from random import randint
from math import ceil, floor
from datetime import datetime
from pytz import timezone

from gemini import *
from calendarAPI import *

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents) #! hello"


@bot.event
async def on_ready():
    print(f"ASA Bot is ready to work! {bot.user.name}")
    global repost_channel
    global birthday_channel
    global bot_guild

    with open('guild_channels.json', 'r') as f:
        guild_channels = json.load(f)

    repost_channel = bot.get_channel(guild_channels["repost_channel"])
    birthday_channel = bot.get_channel(guild_channels['birthday_channel'])
    bot_guild = bot.get_guild(guild_channels['bot_guild'])

    main_loop.start()


valid67gifs = ["https://tenor.com/knFBPBaMB4Z.gif", "https://tenor.com/q0WNC9BA9Cr.gif", "https://tenor.com/glbfYP7tYWr.gif", "https://tenor.com/rdtFCkDpIOF.gif", "https://tenor.com/fG1WQ87kpnp.gif"]

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    elif ("67" in message.content or "6 7" in message.content) and not message.mentions:
        await message.reply(valid67gifs[randint(0, len(valid67gifs) - 1)])

    elif message.author.name == "beomgyu._." and bot.user in message.mentions:
        await message.reply(f"Yes my king {message.author.mention}")

    await bot.process_commands(message)


with open('users.json', 'r') as u:
    asa_members = json.load(u)

temp = []
last_day_updated = None
time_to_post = None
skip = True
skipped_event = None

@tasks.loop(hours=1)
async def main_loop():
    next_event = get_next_event()
    global next_event_name
    next_event_name = next_event[0]
    days_remaining = next_event[1]

    if "birthday" in next_event_name.lower():
        birthday_person = asa_members[next_event_name.split("'")[0]]
        await birthday_channel.send(f"{birthday_text()} {bot.get_user(birthday_person)}!!")

    global temp
    global last_day_updated
    global time_to_post
    global skip
    global skipped_event

    if not temp:
        temp = list(asa_members.values())

    if skip:
        if skipped_event != next_event_name:
            skip = not skip
            return
        return

    now = datetime.now(tz=timezone("US/Eastern"))
    if (last_day_updated != now.day and now.hour == time_to_post) or not last_day_updated or not time_to_post:
        last_day_updated = now.day
        time_to_post = randint(10, 13)

        num_of_reposters = len(temp) / days_remaining
        num_of_reposters = ceil(num_of_reposters) if randint(0, 1) == 0 else floor(num_of_reposters)

        selected_reposters = []
        for _ in range(num_of_reposters):
            selected_reposter = randint(0, len(temp) - 1)
            selected_reposters.append(temp[selected_reposter])
            temp.pop(selected_reposter)

        result_str = ""
        for x in selected_reposters:
            try:
                user_to_mention = bot_guild.get_member(x).mention
            except AttributeError:
                user_to_mention = bot_guild.get_role(x).mention
            
            result_str += f"{user_to_mention} "

        await repost_channel.send(f"{result_str}\n Please repost **{next_event_name}**.")

@bot.command()
async def skip_event(ctx):
    global skip
    global skipped_event
    skip = not skip
    skipped_event = next_event_name

    await ctx.send(f"Repost pings have been set to {skip}")

@bot.command()
async def unskip_event(ctx):
    global skip
    global skipped_event
    skip = not skip
    skipped_event = next_event_name

    await ctx.send(f"Repost pings have been set to {skip}")

if __name__ == '__main__':
    bot.run(token, log_handler=handler, log_level=logging.DEBUG)
