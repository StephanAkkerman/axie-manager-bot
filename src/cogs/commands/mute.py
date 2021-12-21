##> Imports

# > 3rd Party Dependencies
import discord
from discord.ext import commands

# Local dependencies
from config import config


class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role(config["ROLES"]["MANAGER"])
    async def mute(self, ctx, *input):
        """Assign the '[mute]' role to a user

        Usage: `!mute <user>`
        Specify to which user you want to assign the '[mute]' role. This only works when your server has a role named '[mute]' exactly!
        The '[mute]' role should be listed above the role of the mentioned user and the assigned bot role should be listed above the user's.
        To unmute a user, use `!unmute <user>`. For more info, see `!help unmute`.
        """
        # Add role [mute] to mentioned user
        if len(input) == 1:
            try:
                user_id = (
                    int(input[0][3:-1]) if "!" in input[0] else int(input[0][2:-1])
                )
            except Exception:
                raise commands.UserNotFound("")

            try:
                user = ctx.guild.get_member(user_id)
            except Exception:
                raise commands.UserNotFound(user_id)

            if not user:
                raise commands.UserNotFound(user_id)

            role = discord.utils.get(ctx.guild.roles, name="[mute]")
            await user.add_roles(role)
            await ctx.send(f"User **{user.display_name}** has been muted.")
        else:
            raise commands.UserInputError()

    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.message.author.send(
                f"Sorry, you do not have permission to use this command. Please contact a manager if you think that you should."
            )
        elif isinstance(error, commands.UserNotFound):
            await ctx.send(
                f"Sorry, this user could not be found. To find a user, you must mention them. Try again or see `!help mute` for more information."
            )
        elif isinstance(error, commands.UserInputError):
            await ctx.send(
                f"Sorry, you used this command incorrectly. Correct usage is `!mute <user>`. Try again or see `!help mute` for more information."
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

    @commands.command()
    @commands.has_role(config["ROLES"]["MANAGER"])
    async def unmute(self, ctx, *input):
        """Remove the '[mute]' role from a user

        Usage: `!unmute <user>`
        Specify from which user you want to remove the [mute] role.
        """
        # Remove role [mute] from mentioned user
        if len(input) == 1:
            try:
                user_id = (
                    int(input[0][3:-1]) if "!" in input[0] else int(input[0][2:-1])
                )
            except Exception:
                raise commands.UserNotFound("")

            try:
                user = ctx.guild.get_member(user_id)
            except Exception:
                raise commands.UserNotFound(user_id)

            role = discord.utils.get(ctx.guild.roles, name="[mute]")
            await user.remove_roles(role)
            await ctx.send(f"User **{user.display_name}** has been unmuted.")
        else:
            raise commands.UserInputError()

    @unmute.error
    async def unmute_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.message.author.send(
                f"Sorry, you do not have permission to use this command. Please contact a manager if you think that you should."
            )
        elif isinstance(error, commands.UserNotFound):
            await ctx.send(
                f"Sorry, this user could not be found. To find a user, you must mention them. Try again or see `!help unmute` for more information."
            )
        elif isinstance(error, commands.UserInputError):
            await ctx.send(
                f"Sorry, you used this command incorrectly. Correct usage is `!unmute <user>`. Try again or see `!help unmute` for more information."
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
    bot.add_cog(Mute(bot))
