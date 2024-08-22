"""Deadline discord bot"""

import os

from discord.ext import commands
import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from deadline_cog import DeadlineCog
from announcements import update_announcement_scheduler

from dotenv import load_dotenv

# environment variables

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
APPLICATION_ID = os.getenv("APPLICATION_ID")
if not TOKEN:
    raise Exception("No discord token provided")
if not APPLICATION_ID:
    raise Exception("No application id provided")

intents = discord.Intents.default()
intents.message_content = True
intents.typing = False
intents.presences = False

bot = commands.Bot(intents=intents, command_prefix=".", application_id=int(APPLICATION_ID))

bot.scheduler = AsyncIOScheduler()


@bot.event
async def on_ready():
    """when logged in"""
    
    await bot.add_cog(DeadlineCog(bot))
    print(f'We have logged in as {bot.user}')
    await bot.change_presence(status=discord.Status.online, activity=discord.activity.Game("/upcoming"))

    # await update_announcement_scheduler(bot)


bot.run(TOKEN)
