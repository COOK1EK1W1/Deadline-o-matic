"""cog for handling deadline requests"""
import datetime
from typing import Optional
import pytz
import deadlines as dl

from discord.ext import commands

from tabulate import tabulate

def calculate_remaining_time(date: Optional[datetime.datetime]) -> Optional[datetime.datetime]:
    """calculate the remaining time"""
    if date:
        return date - pytz.utc.localize(datetime.datetime.utcnow())
    return None

def calculate_progress(start: Optional[datetime.datetime], end: Optional[datetime.datetime]) -> Optional[float]:
    """calculate current position in deadline"""
    if start and end:
        start_now = pytz.utc.localize(datetime.datetime.utcnow()) - start
        start_end:datetime.timedelta = end - start
        percent = start_now / start_end
        return percent
    return None

def format_progress(percent: Optional[float]) -> str:
    """Turn a percentage to text to be displayed"""
    if not percent:
        return "x"
    if percent < 0:
        return "----- not started -----"
    elif percent > 1:
        return "####### finished #######"
    else :
        return "#" * int(24 * percent) + "-" * int(24 - 24 * percent)


def format_time_delta(delta: datetime.timedelta) -> str:
    """format a delta time into 'x days y hours z minutes'"""
    ##make strings of how long left
    days = ""
    if delta.days > 0:
        days = str(delta.days) + " days"
    hours = ""
    if delta.seconds // 3600 > 0:
        hours = " " + str((delta.seconds // 3600) % 24) + " hours"
    minutes = ""
    if delta.seconds // 60 > 0:
        minutes = " " +str((delta.seconds // 60) % 60) + " minutes"

    return days + hours + minutes



def format_all_deadlines_to_string(deadlines: list[dl.Deadline]) -> str:
    deadline_matrix = []
    for deadline in deadlines:
        course: str = deadline.subject
        name: str = deadline.name

        set_date = deadline.start_datetime

        due_date = deadline.due_datetime

        remaining_time = calculate_remaining_time(due_date)



        deadline_list = [name, course, set_date.strftime("%d %b %H:%M"), due_date.strftime("%d %b %H:%M"), remaining_time]

        deadline_matrix.append(deadline_list)

    return "```" + tabulate(deadline_matrix, headers=["deadline name", "Course", "set on", "due on", "due in"], maxcolwidths=[20, None, None]) + "```" 

class DeadlineCog(commands.Cog, name='Deadlines'):
    """Deadline cog"""

    @commands.command()
    async def all(self, ctx, *_):
        """displays all the deadlines"""
        deadlines = dl.sort_by_due(dl.get_deadlines())
        deadlines = dl.filter_due_after(deadlines, dl.now() - datetime.timedelta(days= 7))
        await ctx.send(embed=dl.format_deadlines_for_embed(deadlines, "All Deadlines"))

    @commands.command()
    async def past(self, ctx, *_):
        """displays past deadlines"""
        deadlines = dl.sort_by_due(dl.get_deadlines())
        deadlines = dl.filter_due_before_now(deadlines)
        await ctx.send(embed=dl.format_deadlines_for_embed(deadlines, "Past Deadlines"))

    @commands.command()
    async def upcoming(self, ctx, *_):
        """display upcoming deadlines"""
        deadlines = dl.sort_by_due(dl.get_deadlines())
        deadlines = dl.filter_due_after_now(deadlines)[:8]
        await ctx.send(embed=dl.format_deadlines_for_embed(deadlines, "Upcoming Deadlines"))

    @commands.command()
    async def thisweek(self, ctx, *_):
        """displays all the deadlines this week"""
        deadlines = dl.sort_by_due(dl.get_deadlines())
        deadlines = dl.filter_due_before(deadlines, dl.now() + datetime.timedelta(days= 6 - datetime.datetime.now().weekday()))
        deadlines = dl.filter_due_after(deadlines, dl.now() - datetime.timedelta(days=datetime.datetime.now().weekday()))
        await ctx.send(embed=dl.format_deadlines_for_embed(deadlines, "Deadlines This Week"))

    @commands.command()
    async def next(self, ctx, *_):
        """displays next deadline"""
        deadlines = dl.sort_by_due(dl.get_deadlines())
        deadlines = dl.filter_due_after_now()
        if len(deadlines) == 0:
            await ctx.send("no deadlines :)")
            return
        await ctx.send(embed=dl.format_deadlines_for_embed([deadlines[0]], "Next Deadline"))

    @commands.command()
    async def all_debug(self, ctx, *_):
        """displays all the deadlines and their sotred values for debugging"""
        deadlines = dl.get_deadlines()
        await ctx.send(format_all_deadlines_to_string(deadlines))
    

    @commands.command()
    async def info(self, ctx, *a):
        """displays all the deadlines and their sotred values for debugging"""
        deadlines = dl.get_deadlines()
        if a == ("next",):
            deadlines = dl.sort_by_due(deadlines)
            deadline = dl.filter_due_after_now(deadlines)[0]
            await ctx.send(embed=deadline.format_for_embed())
        else:
            for x in deadlines:
                if x.name == " ".join(a):
                    await ctx.send(embed=x.format_for_embed())
