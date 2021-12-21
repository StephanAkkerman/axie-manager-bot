##> Imports
# > Discord dependencies
import discord
from discord.ext import commands


class On_command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener(name="on_command")
    async def on_command(self, ctx):
        print(f"{ctx.author} used !{ctx.command} in channel {ctx.message.channel}")


def setup(bot):
    bot.add_cog(On_command(bot))
