import json
from cryptography.fernet import Fernet
from discord.ext import commands

#  Get vars from .json
with open("authentication.json") as f:
    data = json.load(f)

fernet = Fernet(data["KEY"].encode("utf_8"))


class Encrypt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def encrypt(self, ctx, message=None):
        """
        Encrypts a user's message using your personal fernet key
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


def setup(bot):
    bot.add_cog(Encrypt(bot))
