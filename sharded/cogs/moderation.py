from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='test')
    async def test(self, ctx):
        await ctx.send('Test command!')


async def setup(client):
    await client.add_cog(Moderation(client))