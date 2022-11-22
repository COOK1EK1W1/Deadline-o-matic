"""cog for handling deadline requests"""
import datetime
import deadlines as dl

from discord.ext import commands


class DeadlineCog(commands.Cog, name='Deadlines'):
    """Deadline cog"""

    @commands.command()
    async def all(self, ctx, *_):
        """displays all the deadlines"""
        deadlines = dl.sort_by_due(dl.get_deadlines())
        deadlines = dl.filter_due_after(deadlines, dl.now() - datetime.timedelta(days=7))
        if len(deadlines) == 0:
            await ctx.send("no deadlines :)")
            return
        await ctx.send(embed=dl.format_deadlines_for_embed(deadlines, "All Deadlines"))

    @commands.command()
    async def past(self, ctx, *_):
        """displays past deadlines"""
        deadlines = dl.sort_by_due(dl.get_deadlines())
        deadlines = dl.filter_due_before_now(deadlines)
        if len(deadlines) == 0:
            await ctx.send("no deadlines :)")
            return
        await ctx.send(embed=dl.format_deadlines_for_embed(deadlines, "Past Deadlines"))

    @commands.command()
    async def upcoming(self, ctx, *_):
        """display upcoming deadlines"""
        deadlines = dl.sort_by_due(dl.get_deadlines())
        deadlines = dl.filter_due_after_now(deadlines)[:8]
        if len(deadlines) == 0:
            await ctx.send("no deadlines :)")
            return
        await ctx.send(embed=dl.format_deadlines_for_embed(deadlines, "Upcoming Deadlines"))

    @commands.command()
    async def thisweek(self, ctx, *_):
        """displays all the deadlines this week"""
        deadlines = dl.sort_by_due(dl.get_deadlines())
        deadlines = dl.filter_due_before(deadlines, dl.now() + datetime.timedelta(days=6 - datetime.datetime.now().weekday()))
        deadlines = dl.filter_due_after(deadlines, dl.now() - datetime.timedelta(days=datetime.datetime.now().weekday()))
        if len(deadlines) == 0:
            await ctx.send("no deadlines :)")
            return
        await ctx.send(embed=dl.format_deadlines_for_embed(deadlines, "Deadlines This Week"))

    @commands.command()
    async def next(self, ctx, *_):
        """displays next deadline"""
        deadlines = dl.sort_by_due(dl.get_deadlines())
        deadlines = dl.filter_due_after_now(deadlines)
        if len(deadlines) == 0:
            await ctx.send("no deadlines :)")
            return
        await ctx.send(embed=deadlines[0].format_for_embed())

    @commands.command()
    async def all_debug(self, ctx, *_):
        """displays all the deadlines and their sotred values for debugging"""
        deadlines = dl.get_deadlines()
        if len(deadlines) == 0:
            await ctx.send("no deadlines :)")
            return
        await ctx.send(dl.format_all_deadlines_to_string(deadlines))

    @commands.command()
    async def info(self, ctx, *a):
        """display more info for a deadline, use .info next to see the next deadline"""
        deadlines = dl.get_deadlines()
        if a == ("next",):
            deadlines = dl.sort_by_due(deadlines)
            deadline = dl.filter_due_after_now(deadlines)[0]
            await ctx.send(embed=deadline.format_for_embed())
        else:
            for x in deadlines:
                if x.name == " ".join(a):
                    await ctx.send(embed=x.format_for_embed())
