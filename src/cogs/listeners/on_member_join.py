##> Imports
# > Discord dependencies
import discord
from discord.ext import commands

# Import local dependencies
from config import config


class On_member_join(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Gives new users the role Tryout"""
        role = discord.utils.get(
            member.guild.roles, name=config["LISTENERS"]["ON_MEMBER_JOIN"]["ROLE"]
        )
        await member.add_roles(role)


def setup(bot):
    bot.add_cog(On_member_join(bot))
