import requests
import datetime
from tabulate import tabulate
import pytz
import discord


class Programme:
    def __init__(self, data):
        self.id: str = data["code"]
        self.title: str = data["title"]
        self.courses: list[Course] = [Course(self, x) for x in data["courses"]]

    def __repr__(self):
        return f"{self.id} | {self.title} | {len(self.courses)} courses"

    @staticmethod
    def get_from_code(code: str) -> "Programme | None":
        result = requests.get("https://deadline-web.vercel.app/api/" + code)
        json = result.json()
        try:
            return Programme(json)
        except Exception:
            return None

    @staticmethod
    def get_from_guild(guild_id: int) -> "Programme":
        result = requests.get("https://deadline-web.vercel.app/api/d_bound/" + str(guild_id))
        json = result.json()
        return Programme(json)

    def all_deadlines(self):
        deadlines: list[Deadline] = []
        for course in self.courses:
            deadlines += course.deadlines
        return deadlines


class Course:
    def __init__(self, programme: Programme, data):
        self.programme = programme
        self.code: str = data["code"]
        self.title: str = data["title"]
        self.D_emoji: str = data["D_emoji"]
        self.color: str = data["color"]
        self.deadlines = [Deadline(self, x) for x in data["deadlines"]]
        self.course_info: str = data["courseInfo"]
        self.D_announce_channel: str | None = data["D_announce_channel"]


class Deadline:
    def __init__(self, course: Course, data):
        self.course = course
        self.id: int = data["id"]
        self.name: str = data["name"]
        self.course_code: str = data["courseCode"]
        self.type: str = data["type"]
        self.timezone = pytz.timezone("Europe/London")

        if data["start"] is not None:
            self.start: datetime.datetime | None = datetime.datetime.strptime(data["start"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.utc)
        else:
            self.start = None
        if data["due"] is not None:
            self.due: datetime.datetime | None = datetime.datetime.strptime(data["due"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.utc)
        else:
            self.due = None
        self.mark: float = data["mark"]
        self.room: str = data["room"]
        self.url: str = data["url"]
        self.info: str = data["info"]

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
        embed = discord.Embed(title=self.name + " | " + self.course_code, url=self.url, color=0xeb0000)
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



def dt(datetime: datetime.datetime, type: str):
    """return a discord formatted datetime string. R for relative, F for day and time"""
    return "<t:" + str(int(datetime.timestamp())) + ":" + type + ">"



if __name__ == "__main__":
    print(Programme.get_from_code("CS24-4"))
