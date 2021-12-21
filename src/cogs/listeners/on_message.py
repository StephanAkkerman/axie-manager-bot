##> Imports
# > Discord dependencies
import discord
from discord.ext import commands

# Import local dependencies
from config import config


class On_message(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Delete all messages in login channel that are not !qr
        try:
            if not isinstance(message.channel, discord.channel.DMChannel):
                if message.channel.name == config["COMMANDS"]["QR"]["CHANNEL"]:
                    if message.content != "!qr":
                        await message.delete()

        except commands.CommandError as e:
            channel = discord.utils.get(message.guild.channels, name=config["ERROR"])
            await channel.send(
                f"Unhandled error in {message.channel.mention}. User **{message.author.name}#{message.author.discriminator}** caused an error in a message listener. ```{e}```"
            )


def setup(bot):
    bot.add_cog(On_message(bot))
