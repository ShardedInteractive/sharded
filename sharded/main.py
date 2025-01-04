import discord
import os
import logging
# skipcq: PYL-W0622
from rich import print
from rich.panel import Panel
from rich.logging import RichHandler
from rich.console import Console
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime, timezone

log = logging.getLogger("discord")
log.addHandler(RichHandler(markup = True, console = Console()))

load_dotenv()
TOKEN = os.getenv('TOKEN')
DISCORD_PREFIX = os.getenv('DISCORD_PREFIX')
USE_SHARDED_SERVERS = os.getenv('USE_SHARDED_SERVERS')

class Client(commands.Bot):
    async def on_ready(self):
        print(f'{self.user} Logged in successfully!')

intents = discord.Intents.default()
intents.message_content = True

client = Client(intents=intents, command_prefix=DISCORD_PREFIX)

@client.command(help="Find client latency.")
async def ping(ctx):
    embed=discord.Embed(title="Results", description="Pong!", color=0x351aff)
    embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/1319824973233127515/d5059475af7a9aa9def8e2be7ac0c8f3.png?size=1024")
    embed.add_field(name="Latency (ms)", value=f"{round(client.latency * 1000)}ms", inline=True)
    embed.set_footer(text="v0.1.0 Closed BETA | Developed by Sharded Interactive")

    await ctx.send(embed=embed)

@client.command(help="Purges the messages in the channel.")
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):

    if amount >= 100:
        guild_owner_id = ctx.guild.owner_id
        member = await ctx.guild.fetch_member(guild_owner_id)

        now_utc = datetime.now(timezone.utc)
        formatted_time = now_utc.strftime("%H:%M %B %d, %Y")

        embed=discord.Embed(title="Destructive Action", 
                            description=f"A user ran a *destructive action* (purge) and **affected {amount} messages** within one of your servers. We recommend reviewing this invoked action due to the large amount of messages affected. Below is additional information about this action:",
                            color=0x351aff)
        embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/1319824973233127515/d5059475af7a9aa9def8e2be7ac0c8f3.png?size=1024")

        embed.add_field(name="Destructive Action", value="Purge Command", inline=True)
        embed.add_field(name="Affected...", value=f"{amount} messages", inline=True)
        embed.add_field(name="Was ran by...", value=f"<@{ctx.author.id}>", inline=True)
        embed.add_field(name="At... (UTC)", value=formatted_time, inline=True)
        embed.add_field(name="In the discord server...", value=ctx.message.guild.name, inline=True)

        embed.set_footer(text="v0.1.0 Closed BETA | Developed by Sharded Interactive")
        await member.send(embed=embed)


    await ctx.channel.purge(limit=amount)
    await ctx.send(f"Successfully purged {amount} messages.", delete_after=5)

if __name__ == '__main__':
    if not USE_SHARDED_SERVERS:
        print(Panel('Make sure your [yellow].env[/yellow] file is setup properly for the self hosted instance.', title="Warning", expand=False))
    else:
        pass
    client.run(TOKEN, log_handler=RichHandler(markup = True, console = Console()), log_level = logging.INFO)