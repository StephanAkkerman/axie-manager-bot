##> Imports
# > 3rd Party Dependencies
from cryptography.fernet import Fernet

# > Discord dependencies
import discord
from discord.ext import commands

# local dependencies
from config import config

fernet = Fernet(config["COMMANDS"]["ENCRYPT"]["KEY"].encode("utf_8"))


class Encrypt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.dm_only()
    async def encrypt(self, ctx, *input):
        """Encrypt message using your personal fernet key, via a direct message 

        Usage: `!encrypt <message>`
        Send an encrypted message to a user using your personal fernet key.
        _Note_: This only works by sending a direct message to the bot, message following !encrypt should not be empty.
        """

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

    @encrypt.error
    async def encrypt_error(self, ctx, error):
        # Delete this message, to remove clutter
        await ctx.message.delete()

        if isinstance(error, commands.PrivateMessageOnly):
            await ctx.message.author.send(
                "Please only use the `!encrypt` command in private messages for security reasons."
            )
        elif isinstance(error, commands.UserInputError):
            await ctx.message.author.send(
                "Nothing to encrypt. Please type something after `!encrypt` or see `!help encrypt` for more information (do not reply here)."
            )
        else:
            await ctx.message.author.send(
                f"Something went wrong when invoking the _{ctx.command.name}_ command... The managers have been notified of this problem."
            )
            channel = discord.utils.get(
                ctx.guild.channels, name=config["ERROR"]["CHANNEL"]
            )
            await channel.send(
                f"Unhandled error in {ctx.message.channel.mention}. Exception caused by **{ctx.message.author.name}#{ctx.message.author.discriminator}** while invoking the _{ctx.command.name}_ command. \nUser message: `{ctx.message.content}` ```{error}```"
            )


def setup(bot):
    bot.add_cog(Encrypt(bot))
