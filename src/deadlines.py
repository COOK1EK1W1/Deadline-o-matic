import datetime
from tabulate import tabulate
import pytz
import discord
import smart_match

from programme import Deadline


def dt(datetime: datetime.datetime, type: str):
    """return a discord formatted datetime string. R for relative, F for day and time"""
    return "<t:" + str(int(datetime.timestamp())) + ":" + type + ">"


def format_deadlines_for_embed(prog_code: str, deadlines: list[Deadline], heading: str = "") -> discord.Embed:
    """format deadlines for an embed post in discord"""

    embed = discord.Embed(title=heading, color=0xeb0000, url=f"https://deadline-web.vercel.app/{prog_code}")
    for deadline in deadlines:
        due_date = deadline.due
        start_date = deadline.start

        if due_date is not None:
            if start_date is not None and start_date > pytz.utc.localize(datetime.datetime.utcnow()):
                date_string = "starts " + start_date.strftime("%a, %d %b %H:%M") + " ~ " + dt(start_date, "R")
            else:
                date_string = "due " + due_date.strftime("%a, %d %b %H:%M") + " ~ " + dt(due_date, "R")
        else:
            date_string = "tbc"

        strike = ""
        if deadline.due_in_past():
            strike = "~~"

        embed.add_field(name=f"{strike}{deadline.course.D_emoji} {deadline.name} | {deadline.course.code}{strike}", value=date_string + "\n ​", inline=False)  # beware the 0 width space thing used to make empty lines
    return embed


def format_all_deadlines_to_string(deadlines: list[Deadline]) -> str:
    """convert all deadlines to a table in ascci format"""
    deadline_matrix: list[list[str]] = []
    for deadline in deadlines:
        deadline_matrix.append(deadline.format_to_list())
    return "```" + tabulate(deadline_matrix, headers=["deadline name", "Course", "set on", "due on", "due in"], maxcolwidths=[20, None, None])[:1990] + "```"


def get_best_match(deadlines: list[Deadline], match_string: str) -> Deadline | None:
    if len(deadlines) == 0:
        return None 
    results = [[smart_match.similarity(match_string, x.name + " | " + x.subject), x] for x in deadlines]
    results.sort(key=lambda x: x[0], reverse=True)
    return results[0][1]
