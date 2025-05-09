import logging
import discord
from discord import app_commands
from discord.ext import commands
from sharded.config import Environment

log = logging.getLogger("discord")

GUILD_ID = discord.Object(id=int(Environment().vital("GUILD_ID", "static")))
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
    @commands.has_permissions(kick_members=True)
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
    async def ban(self, ctx, member: discord.Member, *, reason: str, blacklist: bool = False):

        if ctx.author.top_role <= member.top_role:
            await ctx.send(
                "You cannot ban a member with a higher or equal role than you.",
                ephemeral=True,
            )
            return
        
        if blacklist:
            class BlacklistModal(discord.ui.Modal, title="Blacklist"):
                reason = discord.ui.TextInput(
                    label="Explanation for blacklisting",
                    style=discord.TextStyle.paragraph,
                    required=True,
                    min_length=30,
                    max_length=500,
                    placeholder="Please provide a detailed reason for blacklisting for review.",
                )

                signature = discord.ui.TextInput(
                    label="Enter your username for confirmation.",
                    style=discord.TextStyle.short,
                    required=True,
                    placeholder="Enter username to certify.",
                )

                async def on_submit(self, interaction: discord.Interaction):
                    # Add the member to the blacklist here
                    log.info(f"Blacklisted {member} for: {self.reason.value}")
                    await interaction.response.send_message(
                        f"{member.mention} has been sent for review for a [possible blacklist.](https://sharded.app)",
                        ephemeral=True,
                    )

            await ctx.interaction.response.send_modal(BlacklistModal())

        await ctx.send(f"Testing ban {member.mention} for: {reason}")

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
