import logging
import discord
from discord import app_commands
from discord.ext import commands
from API.config import Environment

log = logging.getLogger("discord")

GUILD_ID = Environment.vital("GUILD_ID","static")

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='purge', description="Purge a specified amount of messages from the channel.")
    @app_commands.guilds(GUILD_ID)
    @commands.has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, amount: int):
        await interaction.response.send_message("Testing")

async def setup(client):
    await client.add_cog(Moderation(client))