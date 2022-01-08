##> Imports
# > Standard library
from datetime import datetime, timedelta

# > 3rd party dependencies
import pandas as pd
import gspread
import gspread_dataframe as gd

# > Discord dependencies
import discord
from discord.ext import commands

# Local dependencies
from alerts.api import api_game_api_single
from config import config

# Login using the .json file
gc = gspread.service_account(filename="authentication.json")


class ScholarData(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["mystats", "stats", "data"])
    @commands.has_role(config["ROLES"]["SCHOLAR"])
    async def mydata(self, ctx):
        """Request information on your Axie Infinity scholarship account

        Usage: `!mydata`
        Use this command to request some information about your Axie Infinity scholarship account.
        """

        # Open Scholars spreadsheet
        ws = gc.open("Scholars").worksheet("Scholars")
        scholar_info = (
            gd.get_as_dataframe(ws).dropna(axis=0, how="all").dropna(axis=1, how="all")
        )

        try:
            address = scholar_info.loc[
                scholar_info["Scholar Name"] == ctx.message.author.name
            ]["Address"]
        except:
            raise commands.UserNotFound(ctx.message.author.name)

        if not address.empty:
            df = await api_game_api_single(address.tolist()[0])

            # Process data in df
            df["cache_last_updated"] = pd.to_datetime(
                df["cache_last_updated"], unit="ms"
            ).dt.strftime("Updated on: %Y-%m-%d, %H:%M:%S UTC (+8h for PHT)")

            e = discord.Embed(
                title="Your in-game data",
                description="",
                color=0x00FFFF,
            )

            e.set_author(name="Axie Manager", icon_url=self.bot.user.avatar_url)
            e.set_thumbnail(url=self.bot.user.avatar_url)
            e.add_field(
                name="In-game SLP",
                value=str(df["in_game_slp"].tolist()[0]),
                inline=False,
            )

            e.add_field(
                name="MMR",
                value=df["mmr"].tolist()[0],
                inline=False,
            )

            e.add_field(
                name="Rank",
                value=df["rank"].tolist()[0],
                inline=False,
            )

            payout_date = (datetime.now().replace(day=1) + timedelta(days=14)).replace(
                day=14
            )
            if datetime.now() > payout_date:
                # Get next month
                payout_date = (
                    datetime.now().replace(day=1) + timedelta(days=32)
                ).replace(day=14)

            e.add_field(
                name="Next Payout Date",
                value=payout_date.strftime("%Y-%m-%d"),
                inline=False,
            )

            e.add_field(
                name="Days Until Next Payout",
                value=str((payout_date - datetime.now()).days),
                inline=False,
            )

            e.set_footer(text=df["cache_last_updated"].tolist()[0])

            await ctx.message.author.send(embed=e)

        else:
            raise commands.UserNotFound(ctx.message.author.name)

        # Delete this message, to remove clutter
        await ctx.message.delete()

    @mydata.error
    async def mydata_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.message.author.send(
                f"Sorry, you do not have permission to use this command. Please contact a manager if you think that you should."
            )
        elif isinstance(error, commands.UserNotFound):
            print(
                "This user didn't receive their personal data: "
                + ctx.message.author.name
            )
            print("Discord ID : " + str(ctx.message.author.id))
            print("Current time : ", datetime.now().strftime("%H:%M:%S"))
            await ctx.message.author.send(
                f"Sorry, could not find your Discord name in our database. Please contact a manager if you think that this is incorrect."
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

        await ctx.message.delete()


def setup(bot):
    bot.add_cog(ScholarData(bot))
