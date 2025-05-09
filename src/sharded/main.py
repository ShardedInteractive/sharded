import logging
import discord
import os
from discord import app_commands
from rich import print
from rich.logging import RichHandler
from rich.console import Console
from discord.ext import commands
from sharded.config import Environment, Configuration
from sharded.services import Services
from typing import Optional, cast

log = logging.getLogger("discord")
log.handlers = []
log.addHandler(RichHandler(console=Console(), rich_tracebacks=True, markup=True))
log.setLevel(logging.INFO)
log.propagate = False

discord.utils.LOGGING_HANDLER = log.handlers[0]
discord.utils.LOGGING_FORMATTER = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{"
)

for name in [n for n in logging.root.manager.loggerDict if n.startswith("discord.")]:
    logger = logging.getLogger(name)
    logger.handlers, logger.propagate = [log.handlers[0]], False

log.info("Started Sharded logging service")

env = Environment().vital(provider="dynamic")
config = cast(Configuration, Configuration())
services = cast(Services, Services())

DISCORD_TOKEN: str = env["DISCORD_TOKEN"]
DISCORD_PREFIX: str = config.get("sharded", "bot_prefix")
GUILD_ID: discord.Object = discord.Object(id=env["GUILD_ID"])

log.info("Starting Sharded Runtime and additional services...")

try:
    health_status: dict = services.check_health()
    log.info(f"Sharded Services connection successful: {health_status}")
except Exception as e:
    log.error(f"Sharded Services connection failed: {e}")
    raise Exception(
        "Failed to connect to Sharded Services. Please check your internet connection or wait."
    )

class Client(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.remove_command("help")

    async def on_ready(self) -> None:
        print(f"Logged in as {self.user} (ID: {self.user.id})")

        try:
            guild_synced = await self.tree.sync(guild=GUILD_ID)
            guild = self.get_guild(GUILD_ID.id)
            guild_name = guild.name if guild else "Unknown Guild"
            log.info(f"Synced {len(guild_synced)} command(s) to {guild_name}")

        except Exception as e:
            log.error(f"Failed to sync commands: {e}")
            import traceback
            log.error(traceback.format_exc())

        await self.change_presence(activity=discord.Game(name="/help"))

    async def on_guild_join(self, guild: discord.Guild) -> None:
        guild_owner: discord.User = await self.fetch_user(guild.owner_id)

        embed: discord.Embed = discord.Embed(
            title="Hey! Thank you for inviting me to your server!",
            description="To get started, you can use the `/help` command to see a list of available commands.",
            colour=discord.Colour(0x351AFF),
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
            value="Get help or connect with our community at `discord.gg/4BK9vjpg87` or at our GitHub Discussions.",
            inline=False,
        )

        await guild_owner.send(embed=embed)

    async def setup_hook(self) -> None:
        cogs_dir = os.path.join(os.path.dirname(__file__), "cogs")
        for filename in os.listdir(cogs_dir):
            if filename.endswith(".py"):
                try:
                    await self.load_extension(f"sharded.cogs.{filename[:-3]}")
                    log.debug("Loaded extension: %s", filename[:-3])
                except Exception as x:
                    log.error("Failed to load extension %s: %s", filename, x)


intents = discord.Intents.default()
intents.message_content = True
client: Client = Client(intents=intents, command_prefix=DISCORD_PREFIX)


# Commands
@client.hybrid_command(name="ping", description="Give diagnostic information.")
@app_commands.guilds(GUILD_ID)
async def ping(ctx: commands.Context):
    embed = discord.Embed(description="Pong!", colour=discord.Colour(0x351AFF))

    embed.set_thumbnail(
        url="https://cdn.discordapp.com/avatars/1319824973233127515/ecbc1d3cd651a80e764daff2832f8ebe.png?size=1024"
    )
    embed.add_field(
        name="Latency (ms)", value=f"{round(client.latency * 1000)}ms", inline=True
    )
    embed.add_field(name="Guild ID", value=f"{ctx.guild.id}", inline=True)
    embed.add_field(name="Shard", value=f"{ctx.guild.shard_id}", inline=True)

    embed.add_field(name="Session ID", value=f"{client.ws.session_id}", inline=True)

    server_status = services.server_verified(int(ctx.guild.id))
    verified = server_status["verified"]
    verified_name = server_status["name"]
    
    if verified:
        embed.add_field(
            name="Sharded Verification - ✅",
            value=f"Verified as **{verified_name}** for more advanced features and custom support.",
            inline=False,
        )
    else:
        embed.add_field(
            name="Sharded Verification - ❌",
            value="This server is not **Verified** for advanced features. *Visit [sharded.app/verification](https://sharded.app/verification)*",
            inline=False,
        )

    embed.set_footer(text="Developed by Sharded Interactive")
    embed.set_author(
        name="Diagnostic Information",
        url="https://sharded.app"
    )

    await ctx.send(embed=embed)

# Context Menu commands

@client.tree.context_menu(name="User Information", guild=GUILD_ID)
async def user_info(interaction: discord.Interaction, user: discord.Member) -> None:
    guild = client.get_guild(interaction.guild_id) 

    if guild.get_member(user.id) is not None:
        embed_color: discord.Colour = user.accent_color or discord.Colour(0x351AFF)
        embed: discord.Embed = discord.Embed(
            title=f"User Information for {user.display_name}",
            description=f"This user is a guest in the {interaction.guild.name}.",
            colour=embed_color,
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(
            name="Created At",
            value=f"<t:{int(user.created_at.timestamp())}:F>",
            inline=False,
        )
        embed.set_footer(text=f"ID: {user.id} - Developed by Sharded Interactive")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    else:
        highest_role: Optional[discord.Role] = max(
            (role for role in user.roles if role.name != "@everyone"),
            key=lambda r: r.position,
            default=None,
        )
        embed_color: discord.Colour = highest_role.color if highest_role else discord.Colour(0x351AFF)

        embed: discord.Embed = discord.Embed(
            title=f"User Information for {user.display_name}",
            colour=embed_color,
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(
            name="Joined At",
            value=f"<t:{int(user.joined_at.timestamp())}:F>" if user.joined_at else "Unknown",
            inline=False,
        )
        embed.add_field(
            name="Created At",
            value=f"<t:{int(user.created_at.timestamp())}:F>",
            inline=False,
        )

        roles: list[str] = sorted(
            [f"<@&{role.id}>" for role in user.roles if role.name != "@everyone"],
            key=lambda role: next(
                (r.position for r in user.guild.roles if f"<@&{r.id}>" == role), 0
            ),
            reverse=True,
        )
        embed.add_field(
            name=f"`{user.name}` Roles | {len(roles)}",
            value=", ".join(roles) if roles else "No roles",
            inline=False,
        )

        embed.set_footer(text=f"ID: {user.id} - Developed by Sharded Interactive")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

if __name__ == "__main__":
    client.run(
        DISCORD_TOKEN,
        root_logger=True,
        log_handler=RichHandler(markup=True, console=Console()),
    )
