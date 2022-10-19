"""Deadline discord bot"""

from discord.ext import commands
import discord
import os
from deadline_cog import get_deadlines, format_time_delta, get_due_datetime
import asyncio
import datetime
import pytz

from deadline_cog import DeadlineCog

#environment variables
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise Exception("No discord token provided")

ANNOUNCE_CHANNEL = os.getenv("ANNOUNCE_CHANNEL")

bot = commands.Bot(command_prefix=["."])

@bot.event
async def on_ready():
    """when logged in"""
    print(f'We have logged in as {bot.user}')
    print("")
    await bot.change_presence(status=discord.Status.online)

    if not ANNOUNCE_CHANNEL:
        print("no announcement channel, anouncements disabled")
        return

    ###announcement scheduling
    async def announce_deadline(deadline, announce_before: datetime.timedelta):
        deadline_at = get_due_datetime(deadline)
        announce_at = deadline_at - announce_before

        seconds_until_announce = (announce_at - pytz.utc.localize(datetime.datetime.utcnow())).total_seconds()

        if seconds_until_announce < 0:
            return

        print("adding announcement for " + deadline['name'] + " scheduled at " + str(announce_at))
        await asyncio.sleep(seconds_until_announce) #sleep until it has to send the announcement
        channel = bot.get_channel(int(ANNOUNCE_CHANNEL))
        await channel.send(deadline['name'] + " is due in" + format_time_delta(announce_before))


    loop = asyncio.get_event_loop()
    ##run all the announcements
    for deadline in get_deadlines():
        loop.create_task(announce_deadline(deadline, datetime.timedelta(minutes=30)))
        loop.create_task(announce_deadline(deadline, datetime.timedelta(days=1)))


bot.add_cog(DeadlineCog(bot))
bot.run(TOKEN)
