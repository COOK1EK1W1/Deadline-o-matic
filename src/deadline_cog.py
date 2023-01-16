"""cog for handling deadline requests"""
import deadlines as dl
from discord.ext import commands
import discord

from discord import app_commands
from sql_interface import query, q_deadlines


class DeadlineCog(commands.Cog, name='Deadlines'):
    """Deadline cog"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def sync(self, ctx) -> None:
        await ctx.send(f'syncing')
        fmt = await ctx.bot.tree.sync()

        await ctx.send(f'Synced {len(fmt)} commands.')

    @app_commands.command(name="all")
    async def all_slash(self, interaction: discord.Interaction) -> None:
        """displays all the deadlines"""
        deadlines = q_deadlines("SELECT * FROM deadlines")
        if len(deadlines) == 0:
            await interaction.response.send_message("no deadlines :)")
            return
        await interaction.response.send_message(embed=dl.format_deadlines_for_embed(deadlines, "All Deadlines"))

    @app_commands.command(name="past")
    async def past_slash(self, interaction: discord.Interaction):
        """displays past deadlines"""
        deadlines = q_deadlines("SELECT * FROM deadlines WHERE due < CURRENT_DATE()")
        if len(deadlines) == 0:
            await interaction.response.send_message("no deadlines :)")
            return
        await interaction.response.send_message(embed=dl.format_deadlines_for_embed(deadlines, "Past Deadlines"))

    @app_commands.command(name="upcoming")
    async def upcoming_slash(self, interaction: discord.Interaction):
        """display upcoming deadlines"""
        deadlines = q_deadlines("SELECT * FROM deadlines WHERE due > CURRENT_DATE()")[:8]
        if len(deadlines) == 0:
            await interaction.response.send_message("no deadlines :)")
            return
        await interaction.response.send_message(embed=dl.format_deadlines_for_embed(deadlines, "Upcoming Deadlines"))

    @app_commands.command(name="thisweek")
    async def thisweek_slash(self, interaction: discord.Interaction):
        """displays all the deadlines this week"""
        deadlines = q_deadlines("SELECT * FROM deadlines WHERE YEARWEEK(due, 1) = YEARWEEK(CURDATE(), 1)")
        if len(deadlines) == 0:
            await interaction.response.send_message("no deadlines :)")
            return
        await interaction.response.send_message(embed=dl.format_deadlines_for_embed(deadlines, "Deadlines This Week"))

    @app_commands.command(name="next")
    async def next_slash(self, interaction: discord.Interaction):
        """displays next deadline"""
        deadlines = q_deadlines("SELECT * FROM deadlines WHERE due > CURRENT_DATE()")
        if len(deadlines) == 0:
            await interaction.response.send_message("no deadlines :)")
            return
        await interaction.response.send_message(embed=deadlines[0].format_for_embed())

    @app_commands.command(name="all_debug")
    async def all_debug_slash(self, interaction: discord.Interaction):
        """displays all the deadlines and their sotred values for debugging"""
        deadlines = q_deadlines("SELECT * FROM deadlines")
        if len(deadlines) == 0:
            await interaction.response.send_message("no deadlines :)")
            return
        await interaction.response.send_message(dl.format_all_deadlines_to_string(deadlines))

    @app_commands.command(name="info")
    async def info_slash(self, interation: discord.Interaction, searchterm: str):
        """display more info for a deadline, use .info next to see the next deadline"""
        if searchterm == ("next",):
            deadlines = q_deadlines("SELECT * FROM deadlines WHERE due > CURRENT_DATE()")
            if len(deadlines) == 0:
                await interation.response.send_message("no deadlines :)")
            else:
                await interation.response.send_message(embed=deadlines[0].format_for_embed())
        else:
            deadlines = q_deadlines("SELECT * FROM deadlines")
            best_match = dl.get_best_match(deadlines, searchterm)
            if best_match is None:
                await interation.response.send_message("no deadlines :)")
                return
            await interation.response.send_message(embed=best_match.format_for_embed())

    @app_commands.command()
    @app_commands.describe(name="The name of the deadline", 
        course="The course code for the course/subject", 
        start="The date and time when the deadline begins YYYY/MM/DD HH:MM:SS",
        due="The date and time when the deadline ends YYYY/MM/DD HH:MM:SS",
        mark="the maximum amount of mark achievable",
        room="the name and/or room number where you should be for the deadline",
        url="a url relating to the deadline",
        info="any extra information relating to the deadline")
    async def add(self, interaction: discord.Interaction, name: str, course: str, start: str=None, due: str=None, mark: float=0.0, room: str="", url: str="", info: str=""):
        """add a deadline"""
        query("""INSERT INTO deadlines
(name, subject, `start`, due, mark, room, url, info)
VALUES(%s, %s, %s, %s, %s, %s, %s, %s);""", (name, course, start, due, mark, room, url, info))
        await interaction.response.send_message("deadline added")

    @app_commands.command()
    async def remove(self, intertaction: discord.Interaction, name: str):
        deadlines = q_deadlines("SELECT * FROM deadlines")
        best_match = dl.get_best_match(deadlines, name)
        query("DELETE FROM deadlines WHERE name=%s AND subject=%s", (best_match.name, best_match.subject))
        await intertaction.response.send_message("removed")
    

    @commands.command()
    async def all(self, ctx) -> None:
        """displays all the deadlines"""
        await ctx.send("please use `/all` as . commands will be depricated soon")
        deadlines = q_deadlines("SELECT * FROM deadlines")
        if len(deadlines) == 0:
            await ctx.send("no deadlines :)")
            return
        await ctx.send(embed=dl.format_deadlines_for_embed(deadlines, "All Deadlines"))

    @commands.command()
    async def past(self, ctx):
        """displays past deadlines"""
        await ctx.send("please use `/past` as . commands will be depricated soon")
        deadlines = q_deadlines("SELECT * FROM deadlines WHERE due < CURRENT_DATE()")
        if len(deadlines) == 0:
            await ctx.send("no deadlines :)")
            return
        await ctx.send(embed=dl.format_deadlines_for_embed(deadlines, "Past Deadlines"))

    @commands.command()
    async def upcoming(self, ctx):
        """display upcoming deadlines"""
        await ctx.send("please use `/upcoming` as . commands will be depricated soon")
        deadlines = q_deadlines("SELECT * FROM deadlines WHERE due > CURRENT_DATE()")[:8]
        if len(deadlines) == 0:
            await ctx.send("no deadlines :)")
            return
        await ctx.send(embed=dl.format_deadlines_for_embed(deadlines, "Upcoming Deadlines"))

    @commands.command()
    async def thisweek(self, ctx):
        """displays all the deadlines this week"""
        await ctx.send("please use `/thisweek` as . commands will be depricated soon")
        deadlines = q_deadlines("SELECT * FROM deadlines WHERE YEARWEEK(due, 1) = YEARWEEK(CURDATE(), 1)")
        if len(deadlines) == 0:
            await ctx.send("no deadlines :)")
            return
        await ctx.send(embed=dl.format_deadlines_for_embed(deadlines, "Deadlines This Week"))

    @commands.command()
    async def next(self, ctx):
        """displays next deadline"""
        await ctx.send("please use `/next` as . commands will be depricated soon")
        deadlines = q_deadlines("SELECT * FROM deadlines WHERE due > CURRENT_DATE()")
        if len(deadlines) == 0:
            await ctx.send("no deadlines :)")
            return
        await ctx.send(embed=deadlines[0].format_for_embed())

    @commands.command()
    async def all_debug(self, ctx):
        """displays all the deadlines and their sotred values for debugging"""
        await ctx.send("please use `/all_debug` as . commands will be depricated soon")
        deadlines = q_deadlines("SELECT * FROM deadlines")
        if len(deadlines) == 0:
            await ctx.send("no deadlines :)")
            return
        await ctx.send(dl.format_all_deadlines_to_string(deadlines))
