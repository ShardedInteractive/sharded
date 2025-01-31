import logging
import discord
from discord import app_commands
from discord.ext import commands
from API.config import Environment

log = logging.getLogger("discord")

GUILD_ID = Environment.load_key("GUILD_ID", "static")

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='test', description="A test command")
    @app_commands.guilds(GUILD_ID)
    async def test(self, interaction: discord.Interaction):
        log.info("Test command executed")
        await interaction.response.send_message('Test command!')

async def setup(client):
    await client.add_cog(Moderation(client))