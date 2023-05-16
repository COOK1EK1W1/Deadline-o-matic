import deadlines as dl
import datetime
import random
from sql_interface import q_deadlines


async def send_announcement_start(deadline: dl.Deadline, channel, for_time: datetime.datetime):
    embed = deadline.format_for_embed()
    await channel.send(deadline.name + " starts " + dl.dt(deadline.start_datetime, "R"), embed=embed)

    
async def send_announcement_due(deadline: dl.Deadline, channel, for_time: datetime.datetime):
    embed = deadline.format_for_embed()
    await channel.send(deadline.name + " is due " + dl.dt(deadline.due_datetime, "R"), embed=embed)


async def update_announcement_scheduler(bot):
    if bot.ANNOUNCE_CHANNEL is None:
        return
    bot.scheduler.remove_all_jobs()
    # run all the announcements
    for deadline in q_deadlines("SELECT * FROM deadlines WHERE due > CURRENT_TIMESTAMP"):
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
