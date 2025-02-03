import logging
import discord
import wavelink
from discord import app_commands
from discord.ext import commands
from API.config import Environment
from typing import cast

log = logging.getLogger("discord")

GUILD_ID = Environment.vital("GUILD_ID","static")

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name='play', description="Play a song with the given query.")
    @app_commands.guilds(GUILD_ID)
    async def play(self, interaction: discord.Interaction, query: str) -> None:
        if not interaction.guild:
            return

        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)

        if not player:
            if not interaction.user.voice:
                await interaction.response.send_message("Please join a voice channel first before using this command.", ephemeral=True)
                return
                
            try:
                player = await interaction.user.voice.channel.connect(cls=wavelink.Player)  # type: ignore
            except discord.ClientException:
                await interaction.response.send_message("I was unable to join this voice channel. Please try again.", ephemeral=True)
                return

        player.autoplay = wavelink.AutoPlayMode.enabled

        if not hasattr(player, "home"):
            player.home = interaction.channel
        elif player.home != interaction.channel:
            await interaction.response.send_message(f"You can only play songs in {player.home.mention}, as the player has already started there.", ephemeral=True)
            return

        tracks: wavelink.Search = await wavelink.Playable.search(query)
        if not tracks:
            await interaction.response.send_message(f"{interaction.user.mention} - Could not find any tracks with that query. Please try again.", ephemeral=True)
            return

        if isinstance(tracks, wavelink.Playlist):
            added: int = await player.queue.put_wait(tracks)
            await interaction.response.send_message(f"Added the playlist **`{tracks.name}`** ({added} songs) to the queue.")
        else:
            track: wavelink.Playable = tracks[0]
            await player.queue.put_wait(track)
            await interaction.response.send_message(f"Added **`{track}`** to the queue.")

        if not player.playing:
            await player.play(player.queue.get(), volume=30)


    @app_commands.command(name='skip', description="Skip the current song.")
    @app_commands.guilds(GUILD_ID)
    async def skip(self, interaction: discord.Interaction) -> None:
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            return

        await player.skip(force=True)
        await interaction.response.send_message("Skipped current song.", ephemeral=True)


    @app_commands.command(name='nightcore', description="Set the filter to a nightcore style.")
    @app_commands.guilds(GUILD_ID)
    async def nightcore(self, interaction: discord.Interaction) -> None:
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            return

        filters: wavelink.Filters = player.filters
        filters.timescale.set(pitch=1.2, speed=1.2, rate=1)
        await player.set_filters(filters)

        await interaction.response.send_message("Nightcore filter applied.", ephemeral=True)


    @app_commands.command(name='toggle', description="Pause or Resume the Player depending on its current state.")
    @app_commands.guilds(GUILD_ID)
    async def toggle(self, interaction: discord.Interaction) -> None:
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            return

        await player.pause(not player.paused)
        await interaction.response.send_message("Playback toggled", ephemeral=True)


    @app_commands.command(name='volume', description="Change the volume of the player.")
    @app_commands.guilds(GUILD_ID)
    async def volume(self, interaction: discord.Interaction, value: int) -> None:
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            return

        await player.set_volume(value)
        await interaction.response.send_message(f"Volume set to {value}%", ephemeral=True)


    @app_commands.command(name='disconnect', description="Disconnect the Player.")
    @app_commands.guilds(GUILD_ID)
    async def disconnect(self, interaction: discord.Interaction) -> None:
        player: wavelink.Player = cast(wavelink.Player, interaction.guild.voice_client)
        if not player:
            return

        await player.disconnect()
        await interaction.response.send_message("Disconnected.", ephemeral=True)

async def setup(client):
    await client.add_cog(Music(client))