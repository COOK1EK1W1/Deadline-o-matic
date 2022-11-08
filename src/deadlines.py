import datetime
import pytz
import json
import discord
from typing import Optional

class Deadline:
    def __init__(self, json: dict[str, str]):
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
        if datetime_str == "":
            return None
        
        else:
            return self.timezone.localize(datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M"))
    
    def due_in_future(self) -> bool:
        return self.due_datetime > self.timezone.localize(datetime.datetime.now())
    
    def due_in_past(self) -> bool:
        return not self.due_in_future()

    def format_for_embed(self) -> discord.Embed:
        due_date = self.due_datetime
        start_date = self.start_datetime
        info = self.info
        embed = discord.Embed(title=self.name + " | " + self.subject, url=self.url, color=0xeb0000)
        if self.mark:
            embed.add_field(name="Mark", value=str(self.mark)+"%", inline=False)
        if self.room:
            embed.add_field(name="Room", value=self.room, inline=False)
        if self.start_datetime:
            embed.add_field(name="Start", value=self.due_datetime.strftime("%m/%d/%Y %H:%M") + "\n" + "<t:" + str(int(self.start_datetime.timestamp())) + ":R>", inline=False)
        if self.due_datetime:
            embed.add_field(name="Due", value=self.due_datetime.strftime("%m/%d/%Y %H:%M") + "\n" + "<t:" + str(int(self.due_datetime.timestamp())) + ":R>", inline=False)
        if self.info:
            embed.add_field(name="Info", value=info, inline=False) 
        return embed


def get_deadlines() -> list[Deadline]:
    with open("data/deadlines.json", "r", encoding="utf-8") as file:
        data =  json.loads(file.read())
        deadlines: list[Deadline] = []
        for deadline in data:
           deadlines.append(Deadline(deadline)) 
        return deadlines

def sort_by_due(deadlines: list[Deadline], reverse: bool=False) -> list[Deadline]:
    deadlines.sort(key=lambda x: x.due_datetime, reverse=reverse)
    return deadlines


def filter_due_after(deadlines: list[Deadline], time):
    return list(filter(lambda x: x.due_datetime > x.timezone.localize(time), deadlines))

def filter_due_before(deadlines: list[Deadline], time):
    return list(filter(lambda x: x.due_datetime < x.timezone.localize(time), deadlines))

def filter_due_after_now(deadlines: list[Deadline]):
    return list(filter(lambda x: x.due_in_future(), deadlines))

def filter_due_before_now(deadlines: list[Deadline]):
    return list(filter(lambda x: x.due_in_past(), deadlines))

def now():
    return datetime.datetime.now()

def format_deadlines_for_embed(deadlines: list[Deadline], heading: str = "") -> discord.Embed:
    """format deadlines for an embed post in discord"""

    embed = discord.Embed(title=heading, color=0xeb0000)
    for deadline in deadlines:
        due_date = deadline.due_datetime
        start_date = deadline.start_datetime

        due_timestamp = int(due_date.timestamp())
        if start_date is not None and start_date > pytz.utc.localize(datetime.datetime.utcnow()):
            start_timestamp = int(start_date.timestamp())
            time_until = " ~ starts <t:" + str(start_timestamp) + ":R>"
        else:
            time_until = " ~ due <t:" + str(due_timestamp) + ":R>"
        
        date_string = due_date.strftime("%a, %d %b %H:%M") + time_until

        strike = ""
        if deadline.due_in_past():
            strike = "~~"

        colours = {"F28ED":":test_tube:", "F28PL":":keyboard:", "F28SG":":classical_building:", "F28WP":":globe_with_meridians:"}
        embed.add_field(name=f"{strike}{colours[deadline.subject]} {deadline.name} | {deadline.subject}{strike}", value=date_string + "\n ​", inline=False)#beware the 0 width space thing used to make empty lines
    return embed



def main():
    deadlines = get_deadlines()
    sort_by_due(deadlines)
    print(deadlines)

if __name__ == "__main__":
    main()