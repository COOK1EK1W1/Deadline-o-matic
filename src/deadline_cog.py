"""cog for handling deadline requests"""
import deadlines as dl
from discord.ext import commands
import discord
import datetime

from discord import app_commands
import sql_interface as sql
from openai import OpenAI
import os
from dotenv import load_dotenv

from programme import Programme

# environment variables

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=API_KEY)


class DeadlineCog(commands.Cog, name='Deadlines'):
    """Deadline cog"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def sync(self, ctx) -> None:
        await ctx.send('syncing')
        fmt = await ctx.bot.tree.sync()

        await ctx.send(f'Synced {len(fmt)} commands.')

    @commands.command()
    async def disclaimer(self, ctx) -> None:
        content = ctx.message.reference.resolved.content
        response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role":"user",
                        "content": f"""We are students at Heriot Watt university, the following comment was made purely for comedic purposes, and in no way reflects our thoughts on other people, and the university.
\"{content}\"
Please write me a disclaimer saying that this comment was written with the sole purpose of comedy. Make the disclaimer relevant to the comment where possible, if not, write a generic statement. Start off by saying \"disclaimer: \" then write the above comment, followed by the disclaimer". Write me only the disclaimer and no other text."""}
            ],
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0

        )
        await ctx.send(response.choices[0].message.content)

    @app_commands.command(name="all")
    async def all(self, interaction: discord.Interaction, search: str | None = None) -> None:
        """displays all the deadlines"""
        programme = Programme.get_from_guild(interaction.guild_id or 0)
        deadlines = programme.all_deadlines()
        if (search):
            deadlines = list(filter(lambda x: (x.course_code == search), deadlines))
        deadlines.sort(key=lambda x: x.due if x.due else 0)
        if len(deadlines) == 0:
            await interaction.response.send_message("no deadlines :)")
            return
        else:
            await interaction.response.send_message(
                embed=dl.format_deadlines_for_embed(programme.id, deadlines, "All Deadlines")
            )

    @app_commands.command(name="guildid")
    async def guildid(self, interaction: discord.Interaction) -> None:
        """get the guild id, for adding to web"""
        await interaction.response.send_message(interaction.guild_id)


    @app_commands.command(name="past")
    async def past(self, interaction: discord.Interaction):
        """displays past deadlines"""
        programme = Programme.get_from_guild(interaction.guild_id or 0)
        deadlines = programme.all_deadlines()
        deadlines = list(filter(lambda x: ((x.due < x.timezone.localize(datetime.datetime.now())) if x.due else False), deadlines))
        deadlines.sort(key=lambda x: x.due if x.due else 0)
        if len(deadlines) == 0:
            await interaction.response.send_message("no deadlines :)")
            return
        await interaction.response.send_message(
            embed=dl.format_deadlines_for_embed(programme.id, deadlines, "Past Deadlines")
        )

    @app_commands.command(name="upcoming")
    async def upcoming(self, interaction: discord.Interaction):
        """display upcoming deadlines"""
        programme = Programme.get_from_guild(interaction.guild_id or 0)
        deadlines = programme.all_deadlines()
        deadlines = list(filter(lambda x: ((x.due > x.timezone.localize(datetime.datetime.now())) if x.due else False), deadlines))
        deadlines.sort(key=lambda x: x.due if x.due else 0)
        deadlines = deadlines[:8]
        if len(deadlines) == 0:
            await interaction.response.send_message("no deadlines :)")
            return
        await interaction.response.send_message(
            embed=dl.format_deadlines_for_embed(programme.id, deadlines, "Upcoming Deadlines")
        )

    @app_commands.command(name="thisweek")
    async def thisweek(self, interaction: discord.Interaction):
        """displays all the deadlines this week"""
        programme = Programme.get_from_guild(interaction.guild_id or 0)
        deadlines = programme.all_deadlines()
        deadlines = list(filter(lambda x: ((x.due > x.timezone.localize(datetime.datetime.now())) if x.due else False), deadlines))
        deadlines = list(filter(lambda x: ((x.due < x.timezone.localize(datetime.datetime.now()) + datetime.timedelta(weeks=1)) if x.due else False), deadlines))
        deadlines.sort(key=lambda x: x.due if x.due else 0)
        if len(deadlines) == 0:
            await interaction.response.send_message("no deadlines :)")
            return
        await interaction.response.send_message(
            embed=dl.format_deadlines_for_embed(programme.id, deadlines, "Deadlines This Week"))

    @app_commands.command(name="next")
    async def next(self, interaction: discord.Interaction):
        """displays next deadline"""
        programme = Programme.get_from_guild(interaction.guild_id or 0)
        deadlines = programme.all_deadlines()
        deadlines = list(filter(lambda x: ((x.due > x.timezone.localize(datetime.datetime.now())) if x.due else False), deadlines))
        deadlines.sort(key=lambda x: x.due if x.due else 0)
        deadlines = deadlines[:1]
        if len(deadlines) == 0:
            await interaction.response.send_message("no deadlines :)")
            return
        await interaction.response.send_message(
            embed=deadlines[0].format_for_embed()
        )

    @app_commands.command(name="all_debug")
    async def all_debug_slash(self, interaction: discord.Interaction):
        """displays all the deadlines and their sotred values for debugging"""
        deadlines = await sql.many_deadlines()
        if len(deadlines) == 0:
            await interaction.response.send_message("no deadlines :)")
            return
        await interaction.response.send_message(
            dl.format_all_deadlines_to_string(deadlines)
        )

    @app_commands.command(name="info")
    async def info_slash(self, interaction: discord.Interaction, searchterm: str):
        """display more info for a deadline, use .info
        next to see the next deadline"""
        if searchterm.lower() == "next":
            programme = Programme.get_from_guild(interaction.guild_id or 0)
            deadlines = programme.all_deadlines()
            deadlines = list(filter(lambda x: ((x.due > x.timezone.localize(datetime.datetime.now())) if x.due else False), deadlines))
            deadlines.sort(key=lambda x: x.due if x.due else 0)
            deadlines = deadlines[:1]
            if len(deadlines) == 0:
                await interaction.response.send_message("no deadlines :)")
            else:
                await interaction.response.send_message(
                    embed=deadlines[0].format_for_embed()
                )
        else:
            programme = Programme.get_from_guild(interaction.guild_id or 0)
            deadlines = programme.all_deadlines()
            best_match = dl.get_best_match(deadlines, searchterm)
            if best_match is None:
                await interaction.response.send_message("no deadlines :)")
                return
            await interaction.response.send_message(
                embed=best_match.format_for_embed()
            )

    # @app_commands.command()
    # @app_commands.describe(name="The name of the deadline",
    #                        course="The course code for the course/subject",
    #                        start="The date and time when the deadline \
    #                        begins YYYY/MM/DD HH:MM:SS",
    #                        due="The date and time when the deadline ends \
    #                         YYYY/MM/DD HH:MM:SS",
    #                        mark="the maximum amount of mark achievable",
    #                        room="the name and/or room number where you \
    #                         should be for the deadline",
    #                        url="a url relating to the deadline",
    #                        info="any extra information relating to the \
    #                         deadline",
    #                        color="the colour for the deadline, shown \
    #                         on the website"
    #                        )
    # async def add(self,
    #               interaction: discord.Interaction,
    #               name: str,
    #               course: str,
    #               due: str,
    #               start: str = None,
    #               mark: float = 0.0,
    #               room: str = "",
    #               url: str = "",
    #               info: str = "",
    #               color: int = 0
    #               ):
    #     """add a deadline"""
    #     start_datetime = datetime.datetime.strptime(start, "%Y/%m/%d %H:%M:%S") if start else None
    #     await sql.create_deadline(data={
    #         'name': name,
    #         'subject': course,
    #         'start': start_datetime,
    #         'due': datetime.datetime.strptime(due, "%Y/%m/%d %H:%M:%S"),
    #         'mark': mark,
    #         'room': room,
    #         'url': url,
    #         'info': info
    #     })
    #     await interaction.response.send_message("deadline added")
    #     await announcements.update_announcement_scheduler(self.bot)

    # @app_commands.command()
    # async def remove(self,
    #                  intertaction: discord.Interaction,
    #                  name: str,
    #                  subject: str
    #                  ):
    #     deadlines = await sql.many_deadlines()
    #     best_match = dl.get_best_match(deadlines, name)
    #     await sql.delete_deadline(where={
    #         'name_subjet': {
    #             'name': best_match.name,
    #             'subject': best_match.subject
    #         }})
    #     await intertaction.response.send_message("removed")
    #     await announcements.update_announcement_scheduler(self.bot)
