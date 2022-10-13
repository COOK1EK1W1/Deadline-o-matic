"""Deadline discord bot"""

from discord.ext import commands
import discord
import os

from deadline_cog import DeadlineCog

TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix=["."])

@bot.event
async def on_ready():
    """when logged in"""
    print(f'We have logged in as {bot.user}')
    await bot.change_presence(status=discord.Status.online)

bot.add_cog(DeadlineCog(bot))
bot.run(TOKEN)
