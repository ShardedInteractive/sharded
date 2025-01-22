import logging
import discord
import os
# skipcq: PYL-W0622
from rich import print
from rich.panel import Panel
from rich.logging import RichHandler
from rich.console import Console
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime, timezone

log = logging.getLogger("discord")
log.handlers = []
log.addHandler(RichHandler(console=Console(), rich_tracebacks=True))
log.setLevel(logging.INFO)
log.propagate = False

discord.utils.LOGGING_HANDLER = log.handlers[0]
discord.utils.LOGGING_FORMATTER = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', '%Y-%m-%d %H:%M:%S', style='{')

for name in [n for n in logging.root.manager.loggerDict if n.startswith('discord.')]:
    logger = logging.getLogger(name)
    logger.handlers, logger.propagate = [log.handlers[0]], False
    cogs = ['cogs.example_cog']
log.info("Started Sharded logging service")

load_dotenv()
log.info("Loaded .env file")

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_PREFIX = os.getenv('DISCORD_PREFIX')
USE_SHARDED_SERVERS = os.getenv('USE_SHARDED_SERVERS')
# GUILD_ID = discord.Object(id=os.getenv('GUILD_ID'))

# Discord Clients and Classes
log.info("Starting Sharded client and runtime")

class Client(commands.Bot):
    async def on_ready(self):
        print(f'{self.user} Logged in successfully!')

    async def on_guild_join(self, guild):
        guild_owner = await self.fetch_user(guild.owner_id)

        embed = discord.Embed(title="Hey! Thank you for inviting me to your server!",
                      description="Learn more and customize your sharded instance by going to [sharded.app](https://sharded.app) and logging in! Get started by doing `/help` or `!help`",
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


    async def setup_hook(self): 
        for filename in os.listdir('./sharded/cogs'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    log.debug('Loaded extension: %s', filename[:-3])
                except Exception as e:
                    log.error('Failed to load extension %s: %s', filename, e)


intents = discord.Intents.default()
intents.message_content = True

client = Client(intents=intents, command_prefix=DISCORD_PREFIX)

class DestructiveConfirmationMenu(discord.ui.View):
    def __init__(self, ctx, author ,timeout: int = 30):
        super().__init__(timeout=timeout)
        self.value = None
        self.ctx = ctx
        self.author = author

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.danger)
    async def yes(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = True
        self.stop()

    @discord.ui.button(label='No', style=discord.ButtonStyle.secondary)
    async def no(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = False
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        if interaction.user.id == self.author.id:
            return True
        else:
            await interaction.response.send_message("You are not the user who initiated this action.", ephemeral=True)
            return False

# Commands

@client.command(help="Pings the bot and returns the latency.")
async def ping(ctx):

    embed=discord.Embed(title="Results", description="Pong!", color=0x351aff)
    embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/1319824973233127515/d5059475af7a9aa9def8e2be7ac0c8f3.png?size=1024")
    embed.add_field(name="Latency (ms)", value=f"{round(client.latency * 1000)}ms", inline=True)
    embed.add_field(name="Guild ID", value=f"{ctx.guild.id}", inline=True)
    embed.add_field(name="Shard", value=f"{ctx.guild.shard_id}", inline=True)

    embed.add_field(name="Session ID", value=f"{client.ws.session_id}", inline=False)

    embed.set_footer(text="v0.1.0 Closed BETA | Developed by Sharded Interactive")

    await ctx.send(embed=embed)

@client.command(help="Purges the messages in the channel.")
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    CM = DestructiveConfirmationMenu(ctx, ctx.author)
    alreadyPurged = False

    amount = amount + 1

    if amount-1 >= 100:

        await ctx.send(f"Are you sure you want to purge {amount-1} messages?", view=CM, delete_after=30)

        if CM.value is None:
            await CM.wait()
            if CM.value:
                alreadyPurged = True
                await ctx.channel.purge(limit=amount)

                guild_owner_id = ctx.guild.owner_id
                member = await ctx.guild.fetch_member(guild_owner_id)

                now_utc = datetime.now(timezone.utc)
                formatted_time = now_utc.strftime("%H:%M %B %d, %Y")

                embed = discord.Embed(title="Destructive Action", 
                                    description=f"A user ran a *destructive action* (purge) and **affected {amount} messages** within one of your servers. We recommend reviewing this action due to the large amount of messages affected. Below is additional information about this action:",
                                    color=0x351aff)
                embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/1319824973233127515/d5059475af7a9aa9def8e2be7ac0c8f3.png?size=1024")

                embed.add_field(name="Destructive Action", value="Purge Command", inline=True)
                embed.add_field(name="Affected...", value=f"{amount-1} messages", inline=True)
                embed.add_field(name="Was ran by...", value=f"<@{ctx.author.id}>", inline=True)
                embed.add_field(name="At... (UTC)", value=formatted_time, inline=True)
                embed.add_field(name="In the discord server...", value=ctx.message.guild.name, inline=True)

                embed.set_footer(text="v0.1.0 Closed BETA | Developed by Sharded Interactive")
                await member.send(embed=embed)

                await ctx.send(f"Successfully purged {amount-1} messages.", delete_after=5)
            else:
                alreadyPurged = True
                await ctx.send("Cancelled purge.", delete_after=30)

    if alreadyPurged is False:
        await ctx.channel.purge(limit=amount)
        await ctx.send(f"Successfully purged {amount-1} messages.", delete_after=5)
    else:
        pass

if __name__ == '__main__':

    if not USE_SHARDED_SERVERS:
        print(Panel('Make sure your [yellow].env[/yellow] file is setup properly for the self hosted instance.', title="Warning", expand=False))
    else:
        pass
    client.run(DISCORD_TOKEN, root_logger=True, log_handler=RichHandler(markup = True, console = Console()))
