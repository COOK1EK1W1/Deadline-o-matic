"""cog for handling deadline requests"""
import json
import datetime
from typing import Optional

from discord.ext import commands

import tabul

def get_deadlines() -> list[dict]:
    """retrieve deadlines from file, returned as json"""
    with open("data/deadlines.json", "r", encoding="utf-8") as file:
        return json.loads(file.read())

def format_datetime_to_string(date: datetime.datetime) -> str:
    """format dateteime object to string representation"""
    return date.strftime("%d %b %H:%M")

def parse_iso_date(date_str: str) -> Optional[datetime.datetime]:
    """if date is not empty create new datetime.datetime instance"""
    if date_str:
        return datetime.datetime.fromisoformat(date_str)
    return None

def datetime_to_str(date: Optional[datetime.datetime]) -> str:
    """if date is not None, convert to string"""
    if date:
        return format_datetime_to_string(date)
    return "tbc"

def make_deadline_time(date: Optional[datetime.datetime], time: str="") -> Optional[datetime.datetime]:
    """add time to datetime object, 23:59 if not defined or the time specified"""
    if date:
        if time:
            parts = time.split(":")
            date += datetime.timedelta(hours=int(parts[0]), minutes=int(parts[1]))
        else:
            date += datetime.timedelta(hours=23, minutes=59)
        return date
    return None

def calculate_remaining_time(date: Optional[datetime.datetime]) -> Optional[datetime.datetime]:
    """calculate the remaining time"""
    if date:
        return date - datetime.datetime.now()
    return None

def remaining_time_str(time: Optional[datetime.datetime]) -> str:
    """convert the reamining time to a string"""
    if time:
        return str(time)[:-10]
    return "tbc"

def calculate_progress(start: Optional[datetime.datetime], end: Optional[datetime.datetime]) -> Optional[float]:
    """calculate current position in deadline"""
    if start and end:
        start_now = datetime.datetime.now() - start
        print(start_now)
        start_end:datetime.timedelta = end - start
        print(start_end)
        percent = start_now / start_end
        return percent
    return None

def format_progress(percent: Optional[float]) -> str:
    """Turn a percentage to text to be displayed"""
    if not percent:
        return "x"
    if percent < 0:
        return "------ not started -----"
    elif percent > 1:
        return "####### finished #######"
    else :
        return "#" * int(24 * percent) + "-" * int(24 - 24 * percent)




def format_all_deadlines_to_string(dealines: list[dict]) -> str:
    deadline_matrix = []
    for deadline in dealines:
        course: str = deadline["subject"]
        name: str = deadline["name"]

        set_date = parse_iso_date(deadline["start date"])

        due_date = parse_iso_date(deadline["due date"])
        due_date = make_deadline_time(due_date, deadline["due time"])


        remaining_time = calculate_remaining_time(due_date)

        progress = calculate_progress(set_date, due_date)



        deadline_list = [name, datetime_to_str(due_date), remaining_time_str(remaining_time), format_progress(progress)]

        deadline_matrix.append(deadline_list)

    return "```" + tabul.tabulate([["deadline name", "due on", "due in", "progress"]], 
                                    deadline_matrix) + "```"


class DeadlineCog(commands.Cog, name='Deadlines'):
    """Deadline cog"""

    @commands.command()
    async def all(self, ctx, *_):
        """template command"""
        deadlines = get_deadlines()
        await ctx.send(format_all_deadlines_to_string(deadlines))
