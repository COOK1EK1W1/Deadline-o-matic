"""Deadline discord bot"""

from discord.ext import commands
import discord
import os
import deadlines
import asyncio
import datetime
import pytz
import deadlines as dl

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
    await bot.change_presence(status=discord.Status.online, activity=discord.activity.Game(".upcoming"))
    
    if not ANNOUNCE_CHANNEL:
        print("no announcement channel, anouncements disabled")
        return

    ###announcement scheduling
    async def announce_deadline(deadline: deadlines.Deadline):
        before_start = deadline.calculate_announce_before_start()
        before_due = deadline.calculate_announce_before_due()
        deadline_start_at = deadline.start_datetime
        deadline_due_at = deadline.due_datetime
        channel = bot.get_channel(int(ANNOUNCE_CHANNEL))
        for announce_at in before_start:

            seconds_until_announce = (announce_at - pytz.utc.localize(datetime.datetime.utcnow())).total_seconds()

            if seconds_until_announce < 0:
                continue

            print("adding announcement for " + deadline.name + " scheduled at " + str(announce_at))
            await asyncio.sleep(seconds_until_announce) #sleep until it has to send the announcement
            await channel.send(deadline.name + " starts " + f"<t:{int(deadline_start_at.timestamp())}:R>")

        for announce_at in before_due:

            seconds_until_announce = (announce_at - pytz.utc.localize(datetime.datetime.utcnow())).total_seconds()

            if seconds_until_announce < 0:
                continue

            print("adding announcement for " + deadline.name + " scheduled at " + str(announce_at))
            await asyncio.sleep(seconds_until_announce) #sleep until it has to send the announcement
            embed = dl.format_single_deadline(deadline)
            await channel.send(deadline.name + " is due " + f"<t:{int(deadline_due_at.timestamp())}:R>", embed=embed)


    loop = asyncio.get_event_loop()
    ##run all the announcements
    for deadline in deadlines.get_deadlines():
        loop.create_task(announce_deadline(deadline))


bot.add_cog(DeadlineCog(bot))
bot.run(TOKEN)
