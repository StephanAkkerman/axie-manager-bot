##> Imports
# > Discord dependencies
import discord
from discord.ext import commands


class On_message(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if not isinstance(message.channel, discord.channel.DMChannel):
                if message.channel.name == "🤖┃login":
                    if message.content != "!qr":
                        await message.delete()

        except commands.CommandError as e:
            channel = discord.utils.get(message.guild.channels, name="🐞┃bot-errors")
            await channel.send(
                f"Unhandled error in {message.channel.mention}. User **{message.author.name}#{message.author.discriminator}** caused an error in a message listener. ```{e}```"
            )


def setup(bot):
    bot.add_cog(On_message(bot))
