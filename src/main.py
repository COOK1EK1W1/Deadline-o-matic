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

bot = commands.Bot(intents=intents, command_prefix=".", application_id="1026458152817918012")

s = sched.scheduler(time.time, time.sleep)

@bot.event
async def on_ready(started_announcements=False):
    """when logged in"""
    
    await bot.add_cog(DeadlineCog(bot), guilds=[discord.Object(id=597140025582419976)])
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
    for deadline in deadlines.get_deadlines():
        for announce_time_start in deadline.calculate_announce_before_start():
            if announce_time_start < deadline.timezone.localize(datetime.datetime.utcnow()):
                continue
            s.enterabs(announce_time_start.timestamp(), 1, send_announcement, (deadline, ANNOUNCE_CHANNEL, deadline.start_datetime))
            print(deadline.name + " scheduled for announece before start at " + str(announce_time_start))
        for announce_time_due in deadline.calculate_announce_before_due():
            if announce_time_due < deadline.timezone.localize(datetime.datetime.utcnow()):
                continue
            s.enterabs(announce_time_due.timestamp(), 1, send_announcement, (deadline, ANNOUNCE_CHANNEL, deadline.due_datetime))
            print(deadline.name + " scheduled for announece before due at " + str(announce_time_due))
    started_announcements = True
    s.run()



bot.run(TOKEN)
