"""cog for handling deadline requests"""
import deadlines as dl
from discord.ext import commands
from sql_interface import query, q_deadlines


class DeadlineCog(commands.Cog, name='Deadlines'):
    """Deadline cog"""

    @commands.command()
    async def all(self, ctx, *_):
        """displays all the deadlines"""
        deadlines = q_deadlines("SELECT * FROM deadlinebot.deadlines WHERE due >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)")
        if len(deadlines) == 0:
            await ctx.send("no deadlines :)")
            return
        await ctx.send(embed=dl.format_deadlines_for_embed(deadlines, "All Deadlines"))

    @commands.command()
    async def past(self, ctx, *_):
        """displays past deadlines"""
        deadlines = q_deadlines("SELECT * FROM deadlinebot.deadlines WHERE due < CURRENT_DATE()")
        if len(deadlines) == 0:
            await ctx.send("no deadlines :)")
            return
        await ctx.send(embed=dl.format_deadlines_for_embed(deadlines, "Past Deadlines"))

    @commands.command()
    async def upcoming(self, ctx, *_):
        """display upcoming deadlines"""
        deadlines = q_deadlines("SELECT * FROM deadlinebot.deadlines WHERE due > CURRENT_DATE()")[:8]
        if len(deadlines) == 0:
            await ctx.send("no deadlines :)")
            return
        await ctx.send(embed=dl.format_deadlines_for_embed(deadlines, "Upcoming Deadlines"))

    @commands.command()
    async def thisweek(self, ctx, *_):
        """displays all the deadlines this week"""
        deadlines = q_deadlines("SELECT * FROM deadlinebot.deadlines WHERE YEARWEEK(due, 1) = YEARWEEK(CURDATE(), 1)")
        if len(deadlines) == 0:
            await ctx.send("no deadlines :)")
            return
        await ctx.send(embed=dl.format_deadlines_for_embed(deadlines, "Deadlines This Week"))

    @commands.command()
    async def next(self, ctx, *_):
        """displays next deadline"""
        deadlines = q_deadlines("SELECT * FROM deadlinebot.deadlines WHERE due > CURRENT_DATE()")
        if len(deadlines) == 0:
            await ctx.send("no deadlines :)")
            return
        await ctx.send(embed=deadlines[0].format_for_embed())

    @commands.command()
    async def all_debug(self, ctx, *_):
        """displays all the deadlines and their sotred values for debugging"""
        deadlines = q_deadlines("SELECT * FROM deadlinebot.deadlines")
        if len(deadlines) == 0:
            await ctx.send("no deadlines :)")
            return
        await ctx.send(dl.format_all_deadlines_to_string(deadlines))

    @commands.command()
    async def info(self, ctx, *a):
        """display more info for a deadline, use .info next to see the next deadline"""
        if a == ("next",):
            deadlines = q_deadlines("SELECT * FROM deadlinebot.deadlines WHERE due > CURRENT_DATE()")
            if len(deadlines) == 0:
                await ctx.send("no deadlines :)")
            else:
                await ctx.send(embed=deadlines[0].format_for_embed())
        else:
            deadlines = q_deadlines("SELECT * FROM deadlinebot.deadlines")
            best_match = dl.get_best_match(deadlines, " ".join(a))
            await ctx.send(embed=best_match.format_for_embed())

    @commands.command()
    async def add(self, ctx, *, args=None):
        args = args.split("-")
        print(args)
        if len(args) < 2:
            return

        name = ""
        course = ""
        start = None
        due = None
        mark = 0
        room = ""
        url = ""
        info = ""
        for i in range(0, len(args)):
            if args[i][:2] == "n=":
                name = args[i][2:]
            elif args[i][:2] == "c=":
                course = args[i][2:]
            elif args[i][:2] == "s=":
                start = args[i][2:]
            elif args[i][:2] == "d=":
                due = args[i][2:]
            elif args[i][:2] == "m=":
                mark = args[i][2:]
            elif args[i][:2] == "r=":
                room = args[i][2:]
            elif args[i][:2] == "u=":
                url = args[i][2:]
            elif args[i][:2] == "i=":
                info = args[i][2:]

        query("""INSERT INTO deadlinebot.deadlines
(name, subject, `start`, due, mark, room, url, info)
VALUES(%s, %s, %s, %s, %s, %s, %s, %s);""", (name, course, start, due, mark, room, url, info))
