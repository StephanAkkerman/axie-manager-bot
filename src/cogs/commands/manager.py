##> Imports
# > Discord dependencies
import discord
from discord.ext import commands

# Local dependencies
from config import config


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role(config["ROLES"]["SCHOLAR"])
    async def manager(self, ctx):
        """Find out who your manager is

        Usage: `!manager`
        With this command you can find out who your manager is! Please, do not message them in this channel but send a DM.
        """

        roles = [
            r.name
            for r in ctx.author.roles
            if r.name
            in [
                "Akkie100",
                "BreakDownzPvp",
                "MrJuggler",
                "unheil",
                "Joepermans",
                "ManDerMannen",
            ]
        ]
        try:
            managers = [
                m.display_name
                for m in ctx.guild.members
                if m.display_name in roles and "Manager" in [r.name for r in m.roles]
            ]
        except Exception:
            raise commands.UserNotFound("")

        if not managers:
            raise commands.UserNotFound("")

        managernames = " and ".join(managers)

        await ctx.reply(
            f"Your manager{' is**' if len(managers) == 1 else 's are**'} {managernames}**! If you want to ask them something, please message them _privately_."
        )

    @manager.error
    async def manager_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.reply(
                f"Sorry, you do not have permission to use this command. Please contact a manager if you think that you should."
            )
        elif isinstance(error, commands.UserNotFound):
            await ctx.send(
                f"Could not find your manager... Have you checked that you have your manager's name assigned to you as role?"
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
    bot.add_cog(Misc(bot))
