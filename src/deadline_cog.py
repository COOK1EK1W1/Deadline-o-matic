"""cog for handling deadline requests"""
import datetime
import deadlines as dl

from discord.ext import commands
import discord

from discord import app_commands


class DeadlineCog(commands.Cog, name='Deadlines'):
    """Deadline cog"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Deadline Cog Loaded")

    @app_commands.command(name="all", description="display all the deadlines")
    async def all(self, interaction: discord.Interaction) -> None:
        """displays all the deadlines"""
        deadlines = dl.sort_by_due(dl.get_deadlines())
        deadlines = dl.filter_due_after(deadlines, dl.now() - datetime.timedelta(days=7))
        if len(deadlines) == 0:
            await interaction.response.send_message("no deadlines :)")
            return
        await interaction.response.send_message(embed=dl.format_deadlines_for_embed(deadlines, "All Deadlines"))

    @commands.command()
    async def sync(self, ctx) -> None:
        print("doing stuff")
        fmt = await ctx.bot.tree.sync(guild=ctx.guild)

        await ctx.send(f'Synced {len(fmt)} commands.')

    @app_commands.command()
    async def past(self, interaction: discord.Interaction):
        """displays past deadlines"""
        deadlines = dl.sort_by_due(dl.get_deadlines())
        deadlines = dl.filter_due_before_now(deadlines)
        if len(deadlines) == 0:
            await interaction.response.send_message("no deadlines :)")
            return
        await interaction.response.send_message(embed=dl.format_deadlines_for_embed(deadlines, "Past Deadlines"))

    @app_commands.command()
    async def upcoming(self, interaction: discord.Interaction):
        """display upcoming deadlines"""
        deadlines = dl.sort_by_due(dl.get_deadlines())
        deadlines = dl.filter_due_after_now(deadlines)[:8]
        if len(deadlines) == 0:
            await interaction.response.send_message("no deadlines :)")
            return
        await interaction.response.send_message(embed=dl.format_deadlines_for_embed(deadlines, "Upcoming Deadlines"))

    @app_commands.command()
    async def thisweek(self, interaction: discord.Interaction):
        """displays all the deadlines this week"""
        deadlines = dl.sort_by_due(dl.get_deadlines())
        deadlines = dl.filter_due_before(deadlines, dl.now() + datetime.timedelta(days=6 - datetime.datetime.now().weekday()))
        deadlines = dl.filter_due_after(deadlines, dl.now() - datetime.timedelta(days=datetime.datetime.now().weekday()))
        if len(deadlines) == 0:
            await interaction.response.send_message("no deadlines :)")
            return
        await interaction.response.send_message(embed=dl.format_deadlines_for_embed(deadlines, "Deadlines This Week"))

    @app_commands.command()
    async def next(self, interaction: discord.Interaction):
        """displays next deadline"""
        deadlines = dl.sort_by_due(dl.get_deadlines())
        deadlines = dl.filter_due_after_now(deadlines)
        if len(deadlines) == 0:
            await interaction.response.send_message("no deadlines :)")
            return
        await interaction.response.send_message(embed=deadlines[0].format_for_embed())

    @app_commands.command()
    async def all_debug(self, interaction: discord.Interaction):
        """displays all the deadlines and their sotred values for debugging"""
        deadlines = dl.get_deadlines()
        if len(deadlines) == 0:
            await interaction.response.send_message("no deadlines :)")
            return
        await interaction.response.send_message(dl.format_all_deadlines_to_string(deadlines))

    @app_commands.command()
    async def info(self, interation: discord.Interaction, searchTerm: str):
        """display more info for a deadline, use .info next to see the next deadline"""
        deadlines = dl.get_deadlines()
        if searchTerm == ("next",):
            deadlines = dl.sort_by_due(deadlines)
            deadline = dl.filter_due_after_now(deadlines)[0]
            await interation.response.send_message(embed=deadline.format_for_embed())
        else:
            best_match = dl.get_best_match(deadlines, " ".join(searchTerm))
            if best_match is None:
                await interation.response.send_message("no deadlines :)")
                return
            await interation.response.send_message(embed=best_match.format_for_embed())
