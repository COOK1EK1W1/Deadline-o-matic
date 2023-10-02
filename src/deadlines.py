import datetime
from tabulate import tabulate
import pytz
import discord
import smart_match


class Deadline:
    def __init__(self, data):
        self.name: str = data.name
        self.subject = data.subject
        self.timezone = pytz.timezone("Europe/London")

        self.start = data.start
        self.due = data.due 
        self.mark = data.mark
        self.room = data.room
        self.url = data.url
        self.info = data.info

    def calculate_announce_before_due(self) -> list[datetime.datetime]:
        """calculate the times at which an announement should be
        made before the due time"""
        before_due = [
            datetime.timedelta(days=1),
            datetime.timedelta(seconds=60 * 30)
        ]

        due_date = self.due
        start_date = self.start
        if due_date is None:
            return []

        announce_times_before_due: list[datetime.datetime] = []

        for delta in before_due:
            time_at_announce = due_date - delta
            if time_at_announce.hour < 8:
                time_at_announce -= datetime.timedelta(days=1)
                time_at_announce = time_at_announce.replace(hour=18, minute=0)
            if time_at_announce.hour > 18:
                time_at_announce = time_at_announce.replace(hour=18, minute=0)
            if start_date is None or time_at_announce > start_date:
                announce_times_before_due.append(time_at_announce)
        return announce_times_before_due

    def calculate_announce_before_start(self) -> list[datetime.datetime]:
        """calculate the times at which an announement should be
        made before the start"""
        before_start = [
            datetime.timedelta(days=1),
            datetime.timedelta(seconds=60 * 30)
        ]
        
        start_date = self.start

        if start_date is None:
            return []

        announce_times_before_start: list[datetime.datetime] = []
        for delta in before_start:
            time_at_announce = start_date - delta
            if time_at_announce.hour < 8:
                time_at_announce -= datetime.timedelta(days=1)
                time_at_announce = time_at_announce.replace(hour=18, minute=0)
            if time_at_announce.hour > 18:
                time_at_announce = time_at_announce.replace(hour=18, minute=0)
            announce_times_before_start.append(time_at_announce)
        return announce_times_before_start

    def due_in_future(self) -> bool:
        """test if the deadline is due in the future"""
        return self.get_due_date_if_exsits() > self.timezone.localize(datetime.datetime.now())

    def due_in_past(self) -> bool:
        """test if the deadline is due in the past"""
        return not self.due_in_future()

    def format_for_embed(self) -> discord.Embed:
        """format the deadline for a discord embed"""
        embed = discord.Embed(title=self.name + " | " + self.subject, url=self.url, color=0xeb0000)
        if self.mark:
            embed.add_field(name="Mark", value=str(self.mark) + "%", inline=False)
        if self.room:
            embed.add_field(name="Room", value=self.room, inline=False)
        if self.start:
            embed.add_field(name="Start", value=dt(self.start, "F") + "\n" + dt(self.start, "R"), inline=False)
        if self.due:
            embed.add_field(name="Due", value=dt(self.due, "F") + "\n" + dt(self.due, "R"), inline=False)
        else:
            embed.add_field(name="Due", value="tbc")
        if self.info:
            embed.add_field(name="Info", value=self.info, inline=False)
        return embed

    def get_due_date_if_exsits(self) -> datetime.datetime:
        """return datetime if exists else return some time in the future"""
        if self.due is not None:
            return self.due
        else:
            return self.timezone.localize(datetime.datetime.now() + datetime.timedelta(days=100 * 365))

    def get_start_date_if_exsits(self) -> datetime.datetime:
        """return datetime if exists else return default time in past"""
        if self.start is not None:
            return self.start
        else:
            return datetime.datetime.fromtimestamp(0)

    def calculate_remaining_time(self) -> datetime.timedelta:
        """calculate the remaining time"""
        return self.get_due_date_if_exsits() - pytz.utc.localize(datetime.datetime.utcnow())

    def format_to_list(self):
        """format all the data to a list"""
        return [self.name, self.subject, self.get_start_date_if_exsits().strftime("%d %b %H:%M"), self.get_due_date_if_exsits().strftime("%d %b %H:%M"), self.calculate_remaining_time()]


def localise(dt, tz):
    if dt is None:
        return None
    return tz.localize(dt)


def dt(datetime: datetime.datetime, type: str):
    """return a discord formatted datetime string. R for relative, F for day and time"""
    return "<t:" + str(int(datetime.timestamp())) + ":" + type + ">"


def format_deadlines_for_embed(deadlines: list[Deadline], heading: str = "") -> discord.Embed:
    """format deadlines for an embed post in discord"""

    embed = discord.Embed(title=heading, color=0xeb0000, url="https://deadline-web.vercel.app")
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

        colours = {"F29FA": ":abacus:", "F29AI": ":brain:", "F29SO": ":classical_building:", "F29DC": ":telephone_receiver:"}
        embed.add_field(name=f"{strike}{colours.get(deadline.subject)} {deadline.name} | {deadline.subject}{strike}", value=date_string + "\n ​", inline=False)  # beware the 0 width space thing used to make empty lines
    return embed

def format_all_deadlines_to_string(deadlines: list[Deadline]) -> str:
    """convert all deadlines to a table in ascci format"""
    deadline_matrix: list[str | float | datetime.timedelta] = []
    for deadline in deadlines:
        deadline_matrix.append(deadline.format_to_list())
    return "```" + tabulate(deadline_matrix, headers=["deadline name", "Course", "set on", "due on", "due in"], maxcolwidths=[20, None, None])[:1990] + "```"


def get_deadlines() -> list[Deadline]:
    """read the deadlines from file"""
    data = query("SELECT * from deadlines")
    if data is None:
      return []
    return [Deadline(x) for x in data]


def get_best_match(deadlines: list[Deadline], match_string: str) -> Deadline | None:
    if len(deadlines) == 0:
        return None 
    results = [[smart_match.similarity(match_string, x.name + " | " + x.subject), x] for x in deadlines]
    results.sort(key=lambda x: x[0], reverse=True)
    return results[0][1]
