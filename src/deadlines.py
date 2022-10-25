import datetime
import pytz
import json
import discord

class Deadline:
    def __init__(self, json: dict[str, str]):
        self.name = json['name']
        self.subject = json['subject']
        timezone = pytz.timezone("europe/london")
        self.start_datetime: datetime.datetime = timezone.localize(datetime.datetime.strptime(json['start-datetime'], "%Y-%m-%d %H:%M"))
        self.due_datetime: datetime.datetime = timezone.localize(datetime.datetime.strptime(json['due-datetime'], "%Y-%m-%d %H:%M"))

    def calculate_announce_times(self):
        before_start = [datetime.timedelta(days=1), datetime.timedelta(seconds=60*30)]
        before_due = [datetime.timedelta(days=1), datetime.timedelta(seconds=60*30)]

        due_date = self.due_datetime
        start_date = self.start_datetime
        if not due_date or not start_date:
            return

        announce_times_before_start: list[datetime.datetime] = []

        for delta in before_start:
            time_at_announce = start_date - delta
            if time_at_announce.hour < 8:
                time_at_announce -= datetime.timedelta(days=1)
                time_at_announce = time_at_announce.replace(hour=18, minute=0)
            if time_at_announce.hour > 18:
                time_at_announce = time_at_announce.replace(hour=18, minute=0)
            announce_times_before_start.append(time_at_announce)
        
        announce_times_before_due: list[datetime.datetime] = []

        for delta in before_due:
            time_at_announce = due_date - delta
            if time_at_announce.hour < 8:
                time_at_announce -= datetime.timedelta(days=1)
                time_at_announce = time_at_announce.replace(hour=18, minute=0)
            if time_at_announce.hour > 18:
                time_at_announce = time_at_announce.replace(hour=18, minute=0)
            if time_at_announce > start_date:
                announce_times_before_due.append(time_at_announce)
        return announce_times_before_start, announce_times_before_due


def get_deadlines() -> list[Deadline]:
    with open("data/deadlines.json", "r", encoding="utf-8") as file:
        data =  json.loads(file.read())
        deadlines: list[Deadline] = []
        for deadline in data:
           deadlines.append(Deadline(deadline)) 
        return deadlines

def sort_by_due(deadlines: list[Deadline], reverse: bool=False) -> list[Deadline]:
    deadlines.sort(key=lambda x: (x.due_datetime - pytz.utc.localize(datetime.datetime.utcnow())).total_seconds(), reverse=reverse)
    return deadlines

def format_deadlines_for_embed(deadlines: list[Deadline], heading: str = "") -> discord.Embed:
    """format deadlines for an embed post in discord"""

    embed = discord.Embed(title=heading, color=0xeb0000)
    for deadline in deadlines:
        due_date = deadline.due_datetime
        start_date = deadline.start_datetime

        due_timestamp = int(due_date.timestamp())
        start_timestamp = int(start_date.timestamp())
        if start_date > pytz.utc.localize(datetime.datetime.utcnow()):
            time_until = " ~ starts <t:" + str(start_timestamp) + ":R>"
        else:
            time_until = " ~ due <t:" + str(due_timestamp) + ":R>"
        
        date_string = due_date.strftime("%a, %d %b %H:%M") + time_until
        
        embed.add_field(name=f"{deadline.name} ~ {deadline.subject}", value=date_string + "\n ​", inline=False)#beware the 0 width space thing used to make empty lines
    return embed



def main():
    deadlines = get_deadlines()
    sort_by_due(deadlines)
    print(deadlines)

if __name__ == "__main__":
    main()