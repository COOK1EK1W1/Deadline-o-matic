"""Deadline discord bot"""

from discord.ext import commands
import discord
import os
import deadlines
import asyncio
import datetime
import pytz
import sched, time
import deadlines as dl
from sql_interface import q_deadlines

from deadline_cog import DeadlineCog

# environment variables
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise Exception("No discord token provided")

ANNOUNCE_CHANNEL = os.getenv("ANNOUNCE_CHANNEL")

intents = discord.Intents.default()
intents.message_content = True
intents.typing = False
intents.presences = False

bot = commands.Bot(intents=intents, command_prefix=".")

s = sched.scheduler(time.time, time.sleep)

@bot.event
async def on_ready(started_announcements=False):
    """when logged in"""

    await bot.add_cog(DeadlineCog(bot))
    print(f'We have logged in as {bot.user}')
    print("")
    await bot.change_presence(status=discord.Status.online, activity=discord.activity.Game(".upcoming"))

    if ANNOUNCE_CHANNEL is None:
        print("no announcement channel, anouncements disabled")
        return

    if started_announcements:
        print("announcements already stated, must have reconnected")
        return

    async def send_announcement(deadline: dl.Deadline, channel, for_time: datetime.datetime):
        embed = deadline.format_for_embed()
        await channel.send(deadline.name + " is due " + dl.dt(for_time, "t"), embed=embed)

    # run all the announcements
    for deadline in q_deadlines("SELECT * FROM deadlines WHERE due > CURRENT_DATE()"):
        loop.create_task(announce_deadline(deadline))
    started_announcements = True


bot.add_cog(DeadlineCog(bot))
bot.run(TOKEN)
