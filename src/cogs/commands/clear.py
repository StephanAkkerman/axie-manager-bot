##> Imports
# > 3rd Party Dependencies
import discord
from discord.ext import commands

# Local dependencies
from config import config


class Clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["purge", "remove", "delete"])
    @commands.has_role(config["ROLES"]["MANAGER"])
    async def clear(self, ctx, *input):
        """Clear an amount of messages [from a user if specified]

        Usage: `!clear <amount> [user]`
        Specify the amount of messages you want to delete. If you want to delete a certain amount of messages by a specific user,
        also specify the user by adding @<username>.
        """
        # Clear x amount of messages from channel
        if len(input) == 1:
            try:
                await ctx.channel.purge(limit=int(input[0]) + 1)
            except Exception:
                raise commands.UserInputError()

        # Clear x amount of messages from user from channel
        elif len(input) == 2:
            try:
                user = self.bot.get_user(int(input[1][3:-1]))
            except Exception:
                raise commands.UserNotFound(input[1][3:-1])

            if not user:
                raise commands.UserNotFound(input[1][3:-1])

            msgs = []
            counter = 0
            async for message in ctx.channel.history(limit=None):
                if message.author == user:
                    try:
                        int(input[0])
                    except:
                        raise commands.UserInputError()
                    if counter < int(input[0]):
                        msgs.append(message)
                        counter += 1
                    else:
                        break

            await ctx.channel.delete_messages(msgs)

        else:
            raise commands.UserInputError()

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.message.author.send(
                f"Sorry, you do not have permission to use this command. Please contact a manager if you think that you should."
            )
        elif isinstance(error, commands.UserNotFound):
            await ctx.send(
                f"Sorry, this user could not be found. To find a user, you must mention them. Try again or see `!help clear` for more information."
            )
        elif isinstance(error, commands.UserInputError):
            await ctx.send(
                f"Sorry, you used this command incorrectly. Correct usage is `!clear <amount> [user]`. Try again or see `!help clear` for more information."
            )
        else:
            await ctx.send(
                f"Something went wrong when invoking the _{ctx.command.name}_ command... The managers have been notified of this problem."
            )
            channel = discord.utils.get(
                ctx.guild.channels, name=config["ERROR"]["CHANNEL"]
            )
            await channel.send(
                f"Unhandled error in {ctx.message.channel.mention}. Exception caused by **{ctx.message.author.name}#{ctx.message.author.discriminator}** while invoking the _{ctx.command.name}_ command. \nUser message: `{ctx.message.content}` ```{error}```"
            )


def setup(bot):
    bot.add_cog(Clear(bot))
