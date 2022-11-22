import datetime
from tabulate import tabulate
import pytz
import json
import discord
from typing import Optional

class Deadline:
    def __init__(self, json: dict[str, str|float]):
        self.name = json['name']
        self.subject = json['subject']
        self.timezone = pytz.timezone("Europe/London")
        
        self.start_datetime = self.str_to_datetime(json['start-datetime'])
        self.due_datetime = self.str_to_datetime(json['due-datetime'])
        self.room = json['room']
        self.url = json['url']
        self.mark = int(json['mark'] * 100)
        self.info = json['info']

    def calculate_announce_before_due(self) -> list[datetime.datetime]:
        """calculate the times at which an announement should be made before the due time"""
        before_due = [datetime.timedelta(days=1), datetime.timedelta(seconds=60*30)]

        due_date = self.due_datetime
        start_date = self.start_datetime
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
        """calculate the times at which an announement should be made before the start"""
        before_start = [datetime.timedelta(days=1), datetime.timedelta(seconds=60*30)]
        start_date = self.start_datetime

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

    def str_to_datetime(self, datetime_str: str) -> Optional[datetime.datetime]:
        """convert a string to a datetime"""
        if datetime_str == "":
            return None
        else:
            return self.timezone.localize(datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M"))
    
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
            embed.add_field(name="Mark", value=str(self.mark)+"%", inline=False)
        if self.room:
            embed.add_field(name="Room", value=self.room, inline=False)
        if self.start_datetime:
            embed.add_field(name="Start", value=dt(self.start_datetime, "F") + "\n" + dt(self.start_datetime, "R"), inline=False)
        if self.due_datetime:
            embed.add_field(name="Due", value=dt(self.due_datetime, "F") + "\n" + dt(self.due_datetime, "R"), inline=False)
        else:
            embed.add_field(name="Due", value="tbc")
        if self.info:
            embed.add_field(name="Info", value=self.info, inline=False) 
        return embed
    
    def get_due_date_if_exsits(self) -> datetime.datetime:
        """return datetime if exists else return some time in the future"""
        if self.due_datetime is not None:
            return self.due_datetime
        else:
            return self.timezone.localize(datetime.datetime.now()+datetime.timedelta(days=100*365))

    def get_start_date_if_exsits(self) -> datetime.datetime:
        """return datetime if exists else return default time in past"""
        if self.start_datetime is not None:
            return self.start_datetime
        else:
            return datetime.datetime.utcfromtimestamp(0)
    
    def calculate_remaining_time(self)-> datetime.timedelta:
        """calculate the remaining time"""
        return self.get_due_date_if_exsits() - pytz.utc.localize(datetime.datetime.utcnow())

    def format_to_list(self):
        """format all the data to a list"""
        return [self.name, self.subject, self.get_start_date_if_exsits().strftime("%d %b %H:%M"), self.get_due_date_if_exsits().strftime("%d %b %H:%M"), self.calculate_remaining_time()]

def dt(datetime: datetime.datetime, type: str):
    """return a discord formatted datetime string. R for relative, F for day and time"""
    return "<t:" + str(int(datetime.timestamp())) + ":" + type + ">"


def sort_by_due(deadlines: list[Deadline], reverse: bool=False) -> list[Deadline]:
    """sort the deadlines in order of due date"""
    deadlines.sort(key=lambda x: x.get_due_date_if_exsits(), reverse=reverse)
    return deadlines


def filter_due_after(deadlines: list[Deadline], time: datetime.datetime) -> list[Deadline]:
    """keep dates which are after a certain time"""
    return list(filter(lambda x: x.get_due_date_if_exsits() > x.timezone.localize(time), deadlines))


def filter_due_before(deadlines: list[Deadline], time: datetime.datetime) -> list[Deadline]:
    """keep dates which are before a certain times"""
    return list(filter(lambda x: x.get_due_date_if_exsits() <= x.timezone.localize(time), deadlines))

def filter_due_after_now(deadlines: list[Deadline]) -> list[Deadline]:
    """keep dates which are due after now"""
    return list(filter(lambda x: x.due_in_future(), deadlines))

def filter_due_before_now(deadlines: list[Deadline]) -> list[Deadline]:
    """keep dates which are due before now"""
    return list(filter(lambda x: x.due_in_past(), deadlines))

def now() -> datetime.datetime:
    """shortcut for datetime of now"""
    return datetime.datetime.now()

def format_deadlines_for_embed(deadlines: list[Deadline], heading: str = "") -> discord.Embed:
    """format deadlines for an embed post in discord"""

    embed = discord.Embed(title=heading, color=0xeb0000)
    for deadline in deadlines:
        due_date = deadline.due_datetime
        start_date = deadline.start_datetime

        if due_date is not None:
            if start_date is not None and start_date > pytz.utc.localize(datetime.datetime.utcnow()):
                time_until = " ~ starts " + dt(start_date, "R")
            else:
                time_until = " ~ due " + dt(due_date, "R")
        else: time_until = ""
            
        if due_date is not None:
            date_string = due_date.strftime("%a, %d %b %H:%M") + time_until
        else:
            date_string = "tbc"

        strike = ""
        if deadline.due_in_past():
            strike = "~~"

        colours = {"F28ED":":test_tube:", "F28PL":":keyboard:", "F28SG":":classical_building:", "F28WP":":globe_with_meridians:"}
        embed.add_field(name=f"{strike}{colours[deadline.subject]} {deadline.name} | {deadline.subject}{strike}", value=date_string + "\n ​", inline=False)#beware the 0 width space thing used to make empty lines
    return embed

def format_all_deadlines_to_string(deadlines: list[Deadline]) -> str:
    """convert all deadlines to a table in ascci format"""
    deadline_matrix: list[str|float|datetime.timedelta] = []
    for deadline in deadlines:
        deadline_matrix.append(deadline.format_to_list())
    return "```" + tabulate(deadline_matrix, headers=["deadline name", "Course", "set on", "due on", "due in"], maxcolwidths=[20, None, None])[:1990] + "```" 

def read_deadlines_to_json():
    """read the deadlines from a file"""
    with open("data/deadlines.json", "r", encoding="utf-8") as file:
        return json.loads(file.read())

def json_to_deadlines(data: list[dict[str, str|float]]) -> list[Deadline]:
    """read the deadlines from file"""
    deadlines: list[Deadline] = []
    for deadline in data:
        deadlines.append(Deadline(deadline)) 
    return deadlines

def get_deadlines() -> list[Deadline]:
    """read the deadlines from file"""
    data = read_deadlines_to_json()
    return json_to_deadlines(data)