import logging
import discord
import os
import wavelink
# skipcq: PYL-W0622
from rich import print
from rich.logging import RichHandler
from rich.console import Console
from discord.ext import commands
from API.config import Environment
from typing import cast

log = logging.getLogger("discord")
log.handlers = []
log.addHandler(RichHandler(console=Console(), rich_tracebacks=True, markup=True))
log.setLevel(logging.INFO)
log.propagate = False

discord.utils.LOGGING_HANDLER = log.handlers[0]
discord.utils.LOGGING_FORMATTER = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', '%Y-%m-%d %H:%M:%S', style='{')

for name in [n for n in logging.root.manager.loggerDict if n.startswith('discord.') or n.startswith('wavelink.')]:
    logger = logging.getLogger(name)
    logger.handlers, logger.propagate = [log.handlers[0]], False
    cogs = ['cogs.moderation']
log.info("Started Sharded logging service")

env = Environment.vital(provider="dynamic")

DISCORD_TOKEN = env["DISCORD_TOKEN"]
DISCORD_PREFIX = env["DISCORD_PREFIX"]
GUILD_ID = env["GUILD_ID"]

# Discord Clients and Classes
log.info("Starting Sharded client and runtime")

class Client(commands.Bot):
    async def on_ready(self):
        print(f'{self.user} Logged in successfully!')

        try:
            synced = await self.tree.sync(guild=GUILD_ID)
            log.warning("Synced %s commands to guild. Performing this action many times could lead to rate limits. ", len(synced))
        except Exception as e:
            log.error("Failed to sync commands to guild: %s", e)

    async def on_guild_join(self, guild):
        guild_owner = await self.fetch_user(guild.owner_id)

        embed = discord.Embed(title="Hey! Thank you for inviting me to your server!",
                      description="Learn more and customize your sharded instance by going to [sharded.app](https://sharded.app) and logging in! Get started by doing `/help`",
                      colour=0x351aff)

        embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/1319824973233127515/d5059475af7a9aa9def8e2be7ac0c8f3.png?size=1024")
        embed.set_footer(text="v0.1.0 Closed BETA | Developed by Sharded Interactive")

        embed.add_field(name="Open-Source",
                        value="Sharded is always open-source and free to self-host, learn more at our [GitHub project.](https://github.com/shardedinteractive/sharded)",
                        inline=False)
        embed.add_field(name="Join our support server!",
                        value="Get help or connect with our community at discord.gg/4BK9vjpg87 or at our GitHub Discussions.",
                        inline=False)

        await guild_owner.send(embed=embed)


    async def setup_hook(self) -> None:

        await wavelink.Pool.connect(nodes=nodes, client=self, cache_capacity=100)

        for filename in os.listdir('./sharded/cogs'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    log.debug('Loaded extension: %s', filename[:-3])
                except Exception as e:
                    log.error('Failed to load extension %s: %s', filename, e)

    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload) -> None:
        log.info("Wavelink Node connected: %r | Resumed: %s", payload.node, payload.resumed)

    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload) -> None:
        player: wavelink.Player | None = payload.player
        if not player:
            return

        original: wavelink.Playable | None = payload.original
        track: wavelink.Playable = payload.track

        embed: discord.Embed = discord.Embed(title="Now Playing")
        embed.description = f"**{track.title}** by `{track.author}`"

        if track.artwork:
            embed.set_image(url=track.artwork)

        if original and original.recommended:
            embed.description += f"\n\n`This track was recommended via {track.source}`"

        if track.album.name:
            embed.add_field(name="Album", value=track.album.name)

        await player.home.send(embed=embed)

intents = discord.Intents.default()
intents.message_content = True
client = Client(intents=intents, command_prefix=DISCORD_PREFIX)

# Commands

@client.tree.command(name="ping", description="Pings the bot and returns the latency.", guild=GUILD_ID)
async def ping(interaction: discord.Interaction):
    embed=discord.Embed(title="Results", description="Pong!", color=0x351aff)

    embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/1319824973233127515/d5059475af7a9aa9def8e2be7ac0c8f3.png?size=1024")
    embed.add_field(name="Latency (ms)", value=f"{round(client.latency * 1000)}ms", inline=True)
    embed.add_field(name="Guild ID", value=f"{interaction.guild_id}", inline=True)
    embed.add_field(name="Shard", value=f"{interaction.guild.shard_id}", inline=True)

    embed.add_field(name="Session ID", value=f"{client.ws.session_id}", inline=False)

    embed.set_footer(text="Managed Enterprise License | Developed by Sharded Interactive")

    await interaction.response.send_message(embed=embed)

if __name__ == '__main__':
    client.run(DISCORD_TOKEN, root_logger=True, log_handler=RichHandler(markup = True, console = Console()))
