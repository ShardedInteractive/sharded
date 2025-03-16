import logging
import discord
from discord import app_commands
from discord.ext import commands
from API.config import Environment

log = logging.getLogger("discord")

GUILD_ID = Environment.vital("GUILD_ID", "static")


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="purge",
        description="Purge a specified amount of messages from the channel.",
    )
    @app_commands.guilds(GUILD_ID)
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(
            f"Purged {len(deleted)} messages from this channel.", ephemeral=True
        )

    @commands.hybrid_command(name="kick", description="Kick a user from the server.")
    @app_commands.guilds(GUILD_ID)
    # @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str):
        if ctx.author.top_role <= member.top_role:
            await ctx.send(
                "You cannot kick a member with a higher or equal role than you.",
                ephemeral=True,
            )
            return
        await member.kick(reason=reason)
        await ctx.send(f"Kicked {member.mention} from the server.")

    @commands.hybrid_command(name="ban", description="Ban a user from the server.")
    @app_commands.guilds(GUILD_ID)
    # @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str):
        # await member.ban(reason=reason)
        await ctx.send(f"Banned {member.mention} from the server for {reason}.")

    @commands.hybrid_command(name="unban", description="Unban a user from the server.")
    @app_commands.guilds(GUILD_ID)
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: str, *, reason: str = None):
        try:
            user = await self.bot.fetch_user(int(user_id))
            await ctx.guild.unban(user, reason=reason)
            await ctx.send(
                f"Successfully unbanned {user.mention}"
                + (f" for: {reason}" if reason else "")
            )
        except discord.NotFound:
            await ctx.send("That user could not be found.")
        except ValueError:
            await ctx.send("Please provide a valid user ID (numbers only).")
        except Exception as e:
            await ctx.send(f"An error occurred while unbanning: {str(e)}")


async def setup(client):
    await client.add_cog(Moderation(client))
