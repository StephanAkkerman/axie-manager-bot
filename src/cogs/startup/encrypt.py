##> Imports
#> Standard Library
import json

#> Own Modules
from errors import *

# > 3rd Party Dependencies
from cryptography.fernet import Fernet

import discord
from discord.ext import commands


#  Get vars from .json
with open("./authentication.json") as f:
    data = json.load(f)

fernet = Fernet(data["KEY"].encode("utf_8"))

class Encrypt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role("Verified")
    async def encrypt(self, ctx, *input):
        """Encrypt message using your personal fernet key

        Usage: `!encrypt <message>`
        Send an encrypted message to a user using your personal fernet key.
        _Note_: Message following !encrypt should not be empty.
        """

        # If the user writes !encrypt followed by something else
        if ctx.channel.name == "🤖┃bots":

            # Error handling
            if len(input) == 0:
                raise commands.UserInputError()

            # Encode private key
            encMessage = fernet.encrypt(" ".join(input).encode())

            # Send a dm
            await ctx.message.author.send(
                "Hi "
                + ctx.message.author.name
                + ", here is your encrypted key:\n"
                + str(encMessage)
            )

            # Delete this message, for privacy
            await ctx.message.delete()

    @encrypt.error
    async def encrypt_error(self, ctx, error):
        # Delete this message, to remove clutter
        await ctx.message.delete()

        if isinstance(error, commands.MissingRole):
            channel = discord.utils.get(ctx.guild.channels, name="👋┃welcome")
            channel_id = channel.id
            await ctx.message.author.send(
                f"Sorry, you cannot use this command yet, since you are not verified. You can get verified in the <#{channel_id}> channel."
            )
        elif isinstance(error, commands.UserInputError):
            await ctx.message.author.send("Nothing to encrypt. Please type something after `!encrypt` or see `!help encrypt` for more information (do not reply here).")
        else:
            await ctx.message.author.send(
                f"Something went wrong when invoking the _{ctx.command.name}_ command... The managers have been notified of this problem."
            )
            channel = discord.utils.get(ctx.guild.channels, name="🐞┃bot-errors")
            await channel.send(
                f"Unhandled error in {ctx.message.channel.mention}. Exception caused by **{ctx.message.author.name}#{ctx.message.author.discriminator}** while invoking the _{ctx.command.name}_ command. \nUser message: `{ctx.message.content}` ```{error}```"
                )


def setup(bot):
    bot.add_cog(Encrypt(bot))
