import datetime
import random
import deadlines as dl
from sql_interface import many_deadlines


async def send_announcement_start(deadline: dl.Deadline, channel, for_time: datetime.datetime):
    embed = deadline.format_for_embed()
    await channel.send(deadline.name + " starts " + dl.dt(deadline.start, "R"), embed=embed)

    
async def send_announcement_due(deadline: dl.Deadline, channel, for_time: datetime.datetime):
    embed = deadline.format_for_embed()
    await channel.send(deadline.name + " is due " + dl.dt(deadline.due, "R"), embed=embed)


async def update_announcement_scheduler(bot):
    if bot.ANNOUNCE_CHANNEL is None:
        return
    bot.scheduler.remove_all_jobs()
    # run all the announcements
    deadlines = await many_deadlines(where={
        'due': {
            'gt': datetime.datetime.now()
        }
      })

    for deadline in [dl.Deadline(x) for x in deadlines]:
        for x in deadline.calculate_announce_before_start():
            if x > deadline.timezone.localize(datetime.datetime.utcnow()):
                uid = random.randint(0, 10000000)
                bot.scheduler.add_job(send_announcement_start, 'date', id=str(uid), run_date=x, args=(deadline, bot.get_channel(int(bot.ANNOUNCE_CHANNEL)), x))

        for x in deadline.calculate_announce_before_due():
            if x > deadline.timezone.localize(datetime.datetime.utcnow()):
                uid = random.randint(0, 10000000)
                bot.scheduler.add_job(send_announcement_due, 'date', id=str(uid), run_date=x, args=(deadline, bot.get_channel(int(bot.ANNOUNCE_CHANNEL)), x))

    if bot.scheduler.state == 0:
        bot.scheduler.start()
