import asyncio
import time
from discord.ext import commands
import datetime
import random

import deadlines as dl
from programme import Programme


async def send_announcement_start(deadline: dl.Deadline, channel, for_time: datetime.datetime):
    embed = deadline.format_for_embed()
    await channel.send(deadline.name + " starts " + dl.dt(deadline.start, "R"), embed=embed)


async def send_announcement_due(deadline: dl.Deadline, channel, for_time: datetime.datetime):
    embed = deadline.format_for_embed()
    await channel.send(deadline.name + " is due " + dl.dt(deadline.due, "R"), embed=embed)


def job(bot: commands.Bot):
    programmes = ["CS24-4", "AW24", "B21M-PHY", "CS24-3"]
    bot.scheduler.remove_all_jobs()
    for programme in programmes:
        programme = Programme.get_from_code(programme)
        if programme is None:
            continue

        print(programme)
        deadlines = programme.all_deadlines()
        for deadline in deadlines:
            if deadline.course.D_announce_channel is None:
                continue
            for x in deadline.calculate_announce_before_start():
                if x > deadline.timezone.localize(datetime.datetime.utcnow()):
                    uid = random.randint(0, 10000000)
                    bot.scheduler.add_job(send_announcement_start, 'date', id=str(uid), run_date=x, args=(deadline, bot.get_channel(int(deadline.course.D_announce_channel)), x))

            for x in deadline.calculate_announce_before_due():
                if x > deadline.timezone.localize(datetime.datetime.utcnow()):
                    uid = random.randint(0, 10000000)
                    bot.scheduler.add_job(send_announcement_due, 'date', id=str(uid), run_date=x, args=(deadline, bot.get_channel(int(deadline.course.D_announce_channel)), x))


def run_updater(bot: commands.Bot):
    while True:
        time.sleep(10)
        job(bot)
        time.sleep(3590)


def run_announcement(bot: commands.Bot):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    if bot.scheduler.state == 0:
        bot.scheduler.start()
    job(bot)
