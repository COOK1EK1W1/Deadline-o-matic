"""Deadline discord bot"""

from discord.ext import commands
import discord
import os
import deadlines
import asyncio
import datetime
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import deadlines as dl
from sql_interface import q_deadlines

from deadline_cog import DeadlineCog

# environment variables
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise Exception("No discord token provided")

ANNOUNCE_CHANNEL = os.getenv("ANNOUNCE_CHANNEL")
APPLICATION_ID = int(os.getenv("APPLICATION_ID"))

intents = discord.Intents.default()
intents.message_content = True
intents.typing = False
intents.presences = False

bot = commands.Bot(intents=intents, command_prefix=".", application_id=APPLICATION_ID)

bot = commands.Bot(intents=intents, command_prefix=".")

@bot.event
async def on_ready(started_announcements=False):
    """when logged in"""
    
    await bot.add_cog(DeadlineCog(bot))
    print(f'We have logged in as {bot.user}')
    await bot.change_presence(status=discord.Status.online, activity=discord.activity.Game("/upcoming"))

    if ANNOUNCE_CHANNEL is None:
        print("no announcement channel, anouncements disabled")
        return

    if started_announcements:
        print("announcements already stated, must have reconnected")
        return

    async def send_announcement_start(deadline: dl.Deadline, channel, for_time: datetime.datetime):
        embed = deadline.format_for_embed()
        await channel.send(deadline.name + " starts " + dl.dt(for_time, "t"), embed=embed)
        
    async def send_announcement_due(deadline: dl.Deadline, channel, for_time: datetime.datetime):
        embed = deadline.format_for_embed()
        await channel.send(deadline.name + " is due " + dl.dt(for_time, "t"), embed=embed)

    scheduler = AsyncIOScheduler()

    # run all the announcements
    for deadline in q_deadlines("SELECT * FROM deadlines WHERE due > CURRENT_DATE()"):
        for x in deadline.calculate_announce_before_start():
            if x > deadline.timezone.localize(datetime.datetime.utcnow()):
                scheduler.add_job(send_announcement_start, 'date', run_date=x, args=(deadline, bot.get_channel(int(ANNOUNCE_CHANNEL)), x))

        for x in deadline.calculate_announce_before_due():
            if x > deadline.timezone.localize(datetime.datetime.utcnow()):
                scheduler.add_job(send_announcement_due, 'date', run_date=x, args=(deadline, bot.get_channel(int(ANNOUNCE_CHANNEL)), x))
            

    scheduler.start()
    started_announcements = True


bot.run(TOKEN)
