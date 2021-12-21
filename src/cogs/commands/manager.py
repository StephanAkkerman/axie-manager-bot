##> Imports
import traceback

# 3rd party dependencies
import gspread
import gspread_dataframe as gd

# > Discord dependencies
import discord
from discord.ext import commands

# Local dependencies
from config import config

# Login using the .json file
gc = gspread.service_account(filename="authentication.json")


class Manager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role(config["ROLES"]["SCHOLAR"])
    async def manager(self, ctx):
        """Find out who your manager is

        Usage: `!manager`
        With this command you can find out who your manager is! Please, do not message them in this channel but send a DM.
        """

        # Open Scholars spreadsheet
        ws = gc.open("Scholars").worksheet("Scholars")
        scholar_info = (
            gd.get_as_dataframe(ws).dropna(axis=0, how="all").dropna(axis=1, how="all")
        )

        try:
            manager = scholar_info.loc[
                scholar_info["Scholar Name"] == ctx.message.author.name
            ]["Manager"].str.split(", ")
        except:
            raise commands.UserNotFound(ctx.message.author.name)

        if not manager.empty:
            # Use , to separate the names
            disc_manager = [
                user.name
                for user in self.bot.get_all_members()
                if user.name in manager.tolist()[0]
            ]
        else:
            raise commands.UserNotFound(ctx.message.author.name)

        if disc_manager == []:
            raise commands.UserNotFound("")

        await ctx.reply(
            f"Your manager{' is**' if len(disc_manager) == 1 else 's are**'} {','.join(disc_manager)}**! If you want to ask them something, please message them _privately_."
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
                f"""Unhandled error in {ctx.message.channel.mention}. Exception caused by **{ctx.message.author.name}#{ctx.message.author.discriminator}** while invoking the _{ctx.command.name}_ command.
                \nUser message: `{ctx.message.content}` ```{traceback.format_exc()}```"""
            )


def setup(bot):
    bot.add_cog(Manager(bot))
