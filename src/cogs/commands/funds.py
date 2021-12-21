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


class Funds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role(config["ROLES"]["MANAGER"])
    async def funds(self, ctx, *input):
        """ Update or add your funds ronin address
        
        Usage: `!funds <ronin address>`
        Replaces or adds you to the funds spreadsheet.
        """

        if len(input) == 1:
            ronin_address = input[0]
        else:
            raise commands.UserInputError()

        ws = gc.open("Scholars").worksheet("Funds")
        funds = (
            gd.get_as_dataframe(ws).dropna(axis=0, how="all").dropna(axis=1, how="all")
        )

        try:
            old_address = funds.loc[funds["Manager"] == ctx.message.author.name][
                "Funds Address"
            ]
        except:
            raise commands.UserNotFound(ctx.message.author.name)

        if not old_address.empty:
            # Update the funds
            funds.loc[
                funds["Manager"] == ctx.message.author.name, "Funds Address"
            ] = ronin_address

        else:
            # Write manager + address to the sheet
            new = {"Manager": ctx.message.author.name, "Funds Address": ronin_address}

            funds = funds.append(new, ignore_index=True)

        # Update the worksheet
        print(funds)
        gd.set_with_dataframe(ws, funds, include_index=False)

    @funds.error
    async def price_error(self, ctx, error):
        if isinstance(error, commands.UserInputError):
            await ctx.send(
                f"Sorry, you used this command incorrectly. Correct usage is `!funds <ronin address>`. Try again or see `!help funds` for more information."
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
    bot.add_cog(Funds(bot))
