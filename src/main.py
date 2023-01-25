"""Deadline discord bot"""

from discord.ext import commands
import discord
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from deadline_cog import DeadlineCog
from announcements import update_announcement_scheduler

# environment variables
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise Exception("No discord token provided")

APPLICATION_ID = int(os.getenv("APPLICATION_ID"))

intents = discord.Intents.default()
intents.message_content = True
intents.typing = False
intents.presences = False

bot = commands.Bot(intents=intents, command_prefix=".", application_id=APPLICATION_ID)

bot.scheduler = AsyncIOScheduler()

bot.ANNOUNCE_CHANNEL = os.getenv("ANNOUNCE_CHANNEL")

@bot.event
async def on_ready(started_announcements=False):
    """when logged in"""
    
    await bot.add_cog(DeadlineCog(bot))
    print(f'We have logged in as {bot.user}')
    await bot.change_presence(status=discord.Status.online, activity=discord.activity.Game("/upcoming"))

    await update_announcement_scheduler(bot)


bot.run(TOKEN)
