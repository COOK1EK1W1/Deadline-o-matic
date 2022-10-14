"""Deadline discord bot"""

from discord.ext import commands
import discord
import os
from deadline_cog import get_deadlines, make_deadline_time, parse_iso_date
import asyncio
import datetime

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
    async def announce_deadline(deadline, announce_before):
        due_date = parse_iso_date(deadline['due date'])
        due_time = deadline['due time']
        deadline_at = make_deadline_time(due_date, due_time)
        announce_at = deadline_at - announce_before

            
        time_until_announce = (announce_at - datetime.datetime.now()).total_seconds()
        if time_until_announce < 0:
            return

        ##make strings of how long left
        days = ""
        if announce_before.days > 0:
            days = str(announce_before.days) + " days"
        hours = ""
        if announce_before.seconds // 3600 > 0:
            hours = " " + str((announce_before.seconds // 3600) % 24) + " hours"
        minutes = ""
        if announce_before.seconds // 60 > 0:
            minutes = " " +str((announce_before.seconds // 60) % 60) + " minutes"


        print("adding announcement for " + deadline['name'] + " scheduled at " + str(announce_at))
        await asyncio.sleep(time_until_announce) #sleep until it has to send the announcement
        channel = bot.get_channel(int(ANNOUNCE_CHANNEL))
        await channel.send(deadline['name'] + " is due in" + days + hours + minutes)


    loop = asyncio.get_event_loop()
    ##run all the announcements
    for deadline in get_deadlines():
        loop.create_task(announce_deadline(deadline, datetime.timedelta(minutes=30)))
        loop.create_task(announce_deadline(deadline, datetime.timedelta(days=1)))


bot.add_cog(DeadlineCog(bot))
bot.run(TOKEN)
