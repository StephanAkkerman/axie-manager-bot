import json
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
    async def encrypt(self, ctx, message=None):
        """ Encrypts a user's message using your personal fernet key
        
            Message following !encrypt should not be empty
        """

        # If the user writes !encrypt followed by something else
        if ctx.channel.name == "🤖┃bots":

            # Error handling
            if message == None:
                await ctx.message.author.send("Please type something after !encrypt")
                return

            # Delete this message, for privacy
            await ctx.message.delete()

            # Encode private key
            encMessage = fernet.encrypt(message.encode())

            # Send a dm
            await ctx.message.author.send(
                "Hi "
                + ctx.message.author.name
                + ", here is your encrypted key:\n"
                + str(encMessage)
            )
            return

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


def setup(bot):
    bot.add_cog(Encrypt(bot))
