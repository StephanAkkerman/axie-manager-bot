##> Imports
# > Standard libraries
from datetime import datetime
import sys

# > 3rd party dependencies
import gspread
import gspread_dataframe as gd
import pandas as pd

# > Discord dependencies
import discord
from discord.ext import commands
from discord.ext.tasks import loop

# > Local dependencies
from alerts.api import api_game_api
from config import config

# Login using the .json file
gc = gspread.service_account(filename="authentication.json")


class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.leaderboard.start()

    @loop(hours=4)
    async def leaderboard(self):
        """Print the current leaderboard in dedicated leaderboard channel"""

        # Get the guild
        guild = discord.utils.get(
            self.bot.guilds,
            name=config["DEBUG"]["GUILD_NAME"]
            if len(sys.argv) > 1 and sys.argv[1] == "-test"
            else config["DISCORD"]["GUILD_NAME"],
        )

        # Open the worksheet of the specified spreadsheet
        ws = gc.open("Scholars").worksheet("Scholars")
        scholar_info = (
            gd.get_as_dataframe(ws).dropna(axis=0, how="all").dropna(axis=1, how="all")
        )

        # Replace ronin: with 0x for API
        scholar_info["Address"] = scholar_info["Address"].str.replace("ronin:", "0x")

        # Get all addresses and join together as a string seperated by commas
        together = ",".join(scholar_info["Address"].tolist())

        # Call all addresses at once and retreive json
        df = await api_game_api(together)

        # Only these columns are important
        df = df[["name", "mmr", "in_game_slp", "last_claim", "cache_last_updated"]]

        # Delete all the NaN values
        df = df.dropna()

        # Process the data
        df["name"] = df["name"].str.split("|").str[-1]
        df["last_claim"] = pd.to_datetime(df["last_claim"], unit="s")
        df["since_last_claim"] = (datetime.now() - df["last_claim"]).dt.days
        df["cache_last_updated"] = pd.to_datetime(df["cache_last_updated"], unit="ms")
        df.loc[df["since_last_claim"] < 1, "since_last_claim"] = 1
        df["avg_slp"] = df["in_game_slp"] / df["since_last_claim"]
        df = df.astype({"avg_slp": int})
        df = df.sort_values(by=["avg_slp", "mmr"], ascending=False)

        latest_update = df["cache_last_updated"].max().strftime("%m/%d/%Y, %H:%M:%S")

        # Convert all columns to string
        df = df.astype(str)

        # Get top player based on avg SLP
        top_slp = df["name"].tolist()[0]

        # Add emojis
        names = df["name"].tolist()

        slp_emoji = discord.utils.get(guild.emojis, name=config["EMOJIS"]["SLP"])

        names[names.index(top_slp)] = f"{slp_emoji} {names[names.index(top_slp)]}"
        names[0] = "🥇" + names[0]
        names[1] = "🥈" + names[1]
        names[2] = "🥉" + names[2]

        scholars = "\n".join(names)
        mmr = "\n".join(df["mmr"].tolist())
        avg_slp = "\n".join(df["avg_slp"].tolist())

        # Send message in discord channel
        channel = discord.utils.get(
            self.bot.get_all_channels(),
            guild__name=config["DEBUG"]["GUILD_NAME"]
            if len(sys.argv) > 1 and sys.argv[1] == "-test"
            else config["DISCORD"]["GUILD_NAME"],
            name=config["LOOPS"]["LEADERBOARD"]["CHANNEL"],
        )

        e = discord.Embed(
            title="Leaderboard",
            description="",
            color=0x00FFFF,
        )

        e.add_field(
            name="Scholar",
            value=scholars,
            inline=True,
        )

        e.add_field(
            name="MMR",
            value=mmr,
            inline=True,
        )

        e.add_field(
            name="Average SLP",
            value=avg_slp,
            inline=True,
        )

        e.set_footer(text=f"Updated on {latest_update}")

        await channel.send(embed=e)


def setup(bot):
    bot.add_cog(Leaderboard(bot))
