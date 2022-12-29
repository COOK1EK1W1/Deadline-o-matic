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
        fmt = await ctx.bot.tree.sync(guild=ctx.guild)

        await ctx.send(f'Synced {len(fmt)} commands.')

    @app_commands.command(name="all", description="display all the deadlines")
    async def all(self, interaction: discord.Interaction) -> None:
        """displays all the deadlines"""
        deadlines = q_deadlines("SELECT * FROM deadlines")
        if len(deadlines) == 0:
            await interaction.response.send_message("no deadlines :)")
            return
        await interaction.response.send_message(embed=dl.format_deadlines_for_embed(deadlines, "All Deadlines"))

    @app_commands.command()
    async def past(self, interaction: discord.Interaction):
        """displays past deadlines"""
        deadlines = q_deadlines("SELECT * FROM deadlines WHERE due < CURRENT_DATE()")
        if len(deadlines) == 0:
            await interaction.response.send_message("no deadlines :)")
            return
        await interaction.response.send_message(embed=dl.format_deadlines_for_embed(deadlines, "Past Deadlines"))

    @app_commands.command()
    async def upcoming(self, interaction: discord.Interaction):
        """display upcoming deadlines"""
        deadlines = q_deadlines("SELECT * FROM deadlines WHERE due > CURRENT_DATE()")[:8]
        if len(deadlines) == 0:
            await interaction.response.send_message("no deadlines :)")
            return
        await interaction.response.send_message(embed=dl.format_deadlines_for_embed(deadlines, "Upcoming Deadlines"))

    @app_commands.command()
    async def thisweek(self, interaction: discord.Interaction):
        """displays all the deadlines this week"""
        deadlines = q_deadlines("SELECT * FROM deadlines WHERE YEARWEEK(due, 1) = YEARWEEK(CURDATE(), 1)")
        if len(deadlines) == 0:
            await interaction.response.send_message("no deadlines :)")
            return
        await interaction.response.send_message(embed=dl.format_deadlines_for_embed(deadlines, "Deadlines This Week"))

    @app_commands.command()
    async def next(self, interaction: discord.Interaction):
        """displays next deadline"""
        deadlines = q_deadlines("SELECT * FROM deadlines WHERE due > CURRENT_DATE()")
        if len(deadlines) == 0:
            await interaction.response.send_message("no deadlines :)")
            return
        await interaction.response.send_message(embed=deadlines[0].format_for_embed())

    @app_commands.command()
    async def all_debug(self, interaction: discord.Interaction):
        """displays all the deadlines and their sotred values for debugging"""
        deadlines = q_deadlines("SELECT * FROM deadlines")
        if len(deadlines) == 0:
            await interaction.response.send_message("no deadlines :)")
            return
        await interaction.response.send_message(dl.format_all_deadlines_to_string(deadlines))

    @app_commands.command()
    async def info(self, interation: discord.Interaction, searchterm: str):
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
    async def add(self, interaction: discord.Interaction, name: str, course: str, start: str=None, due: str=None, mark: float=0.0, room: str="", url: str="", info: str=""):
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