import logging
import discord
import os

# skipcq: PYL-W0622
from rich import print
from rich.logging import RichHandler
from rich.console import Console
from discord.ext import commands
from API.config import Environment, Configuration

log = logging.getLogger("discord")
log.handlers = []
log.addHandler(RichHandler(console=Console(), rich_tracebacks=True, markup=True))
log.setLevel(logging.INFO)
log.propagate = False

discord.utils.LOGGING_HANDLER = log.handlers[0]
discord.utils.LOGGING_FORMATTER = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{"
)

for name in [
    n
    for n in logging.root.manager.loggerDict
    if n.startswith("discord.") or n.startswith("wavelink.")
]:
    logger = logging.getLogger(name)
    logger.handlers, logger.propagate = [log.handlers[0]], False
    cogs = ["cogs.moderation", "cogs.music"]
log.info("Started Sharded logging service")

env = Environment.vital(provider="dynamic")
config = Configuration()

DISCORD_TOKEN = env["DISCORD_TOKEN"]
DISCORD_PREFIX = config.get("sharded", "bot_prefix")
GUILD_ID = env["GUILD_ID"]

# Discord Clients and Classes
log.info("Starting Sharded client and runtime")


class Client(commands.Bot):
    async def on_ready(self):
        print(f"{self.user} Logged in successfully!")

        if config.get("sharded", "sync_application_commands") == "true":
            try:
                synced = await self.tree.sync(guild=GUILD_ID)
                log.warning(
                    "Synced %s commands to guild. Performing this action many times could lead to rate limits. ",
                    len(synced),
                )
            except Exception as e:
                log.error("Failed to sync commands to guild: %s", e)

    async def on_guild_join(self, guild):
        guild_owner = await self.fetch_user(guild.owner_id)

        embed = discord.Embed(
            title="Hey! Thank you for inviting me to your server!",
            description="To get started, you can use the `/help` command to see a list of available commands.",
            colour=0x351AFF,
        )

        embed.set_thumbnail(
            url="https://cdn.discordapp.com/avatars/1319824973233127515/d5059475af7a9aa9def8e2be7ac0c8f3.png?size=1024"
        )
        embed.set_footer(text="Developed by Sharded Interactive")

        embed.add_field(
            name="Open-Source",
            value="Sharded is always open-source and free to self-host, learn more at our [GitHub project.](https://github.com/shardedinteractive/sharded)",
            inline=False,
        )
        embed.add_field(
            name="Join our support server!",
            value="Get help or connect with our community at discord.gg/4BK9vjpg87 or at our GitHub Discussions.",
            inline=False,
        )

        await guild_owner.send(embed=embed)

    async def setup_hook(self) -> None:
        for filename in os.listdir("./sharded/cogs"):
            if filename.endswith(".py"):
                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                    log.debug("Loaded extension: %s", filename[:-3])
                except Exception as e:
                    log.error("Failed to load extension %s: %s", filename, e)


intents = discord.Intents.default()
intents.message_content = True
client = Client(intents=intents, command_prefix=DISCORD_PREFIX)


# Commands
@client.command(
    name="ping",
    description="Pings the bot and returns the latency.",
    with_app_command=True,
)
async def ping(ctx: commands.Context):
    embed = discord.Embed(title="Results", description="Pong!", color=0x351AFF)

    embed.set_thumbnail(
        url="https://cdn.discordapp.com/avatars/1319824973233127515/d5059475af7a9aa9def8e2be7ac0c8f3.png?size=1024"
    )
    embed.add_field(
        name="Latency (ms)", value=f"{round(client.latency * 1000)}ms", inline=True
    )
    embed.add_field(name="Guild ID", value=f"{ctx.guild.id}", inline=True)
    embed.add_field(name="Shard", value=f"{ctx.guild.shard_id}", inline=True)

    embed.add_field(name="Session ID", value=f"{client.ws.session_id}", inline=False)

    embed.set_footer(text="Enterprise License | Developed by Sharded Interactive")

    await ctx.send(embed=embed)


if __name__ == "__main__":
    client.run(
        DISCORD_TOKEN,
        root_logger=True,
        log_handler=RichHandler(markup=True, console=Console()),
    )
