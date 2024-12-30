import discord
import os
# skipcq: PYL-W0622
from rich import print
from rich.panel import Panel
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')

class Client(commands.Bot):
    @staticmethod
    async def on_ready():
        print(f'{client.user} Logged in successfully!')

intents = discord.Intents.default()
intents.message_content = True

client = Client(intents=intents, command_prefix="!")

@client.command(help="Find client latency.")
async def ping(ctx):
    embed=discord.Embed(title="Results", description="Pong!", color=0x351aff)
    embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/1319824973233127515/d5059475af7a9aa9def8e2be7ac0c8f3.png?size=1024")
    embed.add_field(name="Latency (ms)", value=f"{round(client.latency * 1000)}ms", inline=True)
    embed.set_footer(text="v0.1.0 Closed BETA | Developed by Sharded Interactive")

    await ctx.send(embed=embed)

if __name__ == '__main__':
    print(Panel('Make sure your [yellow].env[/yellow] file is setup properly for the self hosted instance.', title="Warning", expand=False))
    client.run(TOKEN)