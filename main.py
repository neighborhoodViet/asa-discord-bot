import discord
from discord.ext import commands, tasks
import logging
from dotenv import load_dotenv
import os

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

valid67gifs = ["https://tenor.com/knFBPBaMB4Z.gif", "https://tenor.com/q0WNC9BA9Cr.gif", "https://tenor.com/glbfYP7tYWr.gif", "https://tenor.com/rdtFCkDpIOF.gif", "https://tenor.com/fG1WQ87kpnp.gif"]

bot = commands.Bot(command_prefix='!', intents=intents) #! hello"

@bot.event
async def on_ready():
    print(f"ASA Bot is ready to work! {bot.user.name}")
    main_loop.start()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    elif ("67" in message.content or "6 7" in message.content):
        await message.reply(valid67gifs[randint(0, len(valid67gifs) - 1)])

    elif message.author.name == "beomgyu._.":
        if randint(0, 20) == 0 or bot.user in message.mentions:
            await message.reply(f"Yes my king {message.author.mention}")

    author_roles = [x.name for x in message.author.roles]

    await bot.process_commands(message)

repost_channel = bot.get_channel(1419688863475040288)
birthday_channel = bot.get_channel(1355030340607017102)
asa_members = {"Jaira": 1405950487622324284, "David": 461679009131003937, "Sakina": 1291219047731433482, "Thien": 477488906489561099, "Cathy": 816122867921453076, "Antinet": 654086056924151808, "An": 531296756613382165, "Uyanga": 755435417993740309, "Clare": 1358923944983531642, "Divya": 1288632175108947968}
temp = []
last_day_updated = None
time_to_post = 11

@tasks.loop(hours=1)
async def main_loop():
    next_event = get_next_event()
    next_event_name = next_event[0]
    days_remaining = next_event[1]

    if "birthday" in next_event_name.lower():
        birthday_person = asa_members[next_event_name.split("'")[0]]
        await birthday_channel.send(f"{birthday_text()} {bot.get_user(birthday_person)}!!")

    global temp
    global last_day_updated
    global time_to_post

    if not temp:
        temp = list(asa_members.values())

    now = datetime.now(tz=timezone("US/Eastern"))
    if last_day_updated != now.day and now.hour == time_to_post:
        last_day_updated = now.day
        time_to_post = randint(10, 13)

        num_of_reposters = len(temp) / days_remaining
        num_of_reposters = ceil(num_of_reposters) if randint(0, 1) == 0 else floor(num_of_reposters)

        selected_reposters = []
        for _ in range(num_of_reposters):
            selected_reposter = randint(0, len(temp) - 1)
            selected_reposters.append(selected_reposter)
            temp.pop(selected_reposter)

        result_str = ""
        for x in selected_reposters:
            result_str += f"{bot.get_user(x).mention or bot.get_guild(1336139315079548999).get_role(x).mention} "

        await repost_channel.send(f"{result_str}\n Please repost {next_event_name}\n {10 - len(selected_reposters)} / 10 remaining")

if __name__ == '__main__':
    bot.run(token, log_handler=handler, log_level=logging.DEBUG)
