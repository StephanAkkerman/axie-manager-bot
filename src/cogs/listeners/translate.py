##> Imports
import sys

# > Discord dependencies
import discord
from discord.ext import commands
from googletrans import Translator, constants

# Import local dependencies
from config import config

# Ready the translator
translator = Translator()


class Translate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):

        # Get the channel
        channel = discord.utils.get(
            self.bot.get_all_channels(),
            guild__name=config["DEBUG"]["GUILD_NAME"]
            if len(sys.argv) > 1 and sys.argv[1] == "-test"
            else config["DISCORD"]["GUILD_NAME"],
            name=config["LISTENERS"]["TRANSLATE"]["CHANNEL"],
        )

        # Ignore bot messages
        if message.author.id != self.bot.user.id:
            translated = translator.detect(message.content)
            if (
                translated.lang == config["LISTENERS"]["TRANSLATE"]["LANGUAGE"]
                and translated.confidence > 0.2
            ):
                translation = translator.translate(message.content, dest="en").text

                # Make a nice embed
                e = discord.Embed(
                    title=f"Translation of {message.author}'s message in {message.channel}",
                    description="",
                )

                e.add_field(name="Original", value=message.content)
                e.add_field(name="Translation", value=translation)

                await channel.send(embed=e)


def setup(bot):
    bot.add_cog(Translate(bot))
