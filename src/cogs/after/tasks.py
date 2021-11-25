##> Imports
# > Standard libraries
import asyncio
from datetime import datetime, timedelta

# > 3rd party dependencies
from dateutil.relativedelta import relativedelta
import gspread
import gspread_dataframe as gd
import pandas as pd

# > Discord dependencies
import discord
from discord.ext import commands
from discord.ext.tasks import loop

# > Local dependencies
from alerts.api import api_game_api

gc = gspread.service_account(filename="authentication.json")


class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.clean_listings.start()
        self.slp_warning.start()
        self.leaderboard.start()

    def delta(self, day, hour, minute):
        """Calculate the amount of seconds until the next day, hour, minute triple"""
        now = datetime.now()
        future = datetime(now.year, now.month, day, hour, minute)

        if now.day >= day:
            future += relativedelta(months=+1)
        elif now.hour >= hour and now.minute > minute:
            future += timedelta(days=1)

        return (future - now).seconds + (future - now).days * 24 * 3600

    @loop(hours=168)
    async def slp_warning(self):
        scholar_info = (
            gd.get_as_dataframe(gc.open("Scholars").worksheet("Scholars"))
            .dropna(axis=0, how="all")
            .dropna(axis=1, how="all")
        )

        # Get all addresses and join together as a string seperated by commas
        together = ",".join(scholar_info["Address"].tolist())

        # Call all addresses at once and retreive json
        df = api_game_api(together).reset_index()

        df["days_since_last_claim"] = datetime.now() - pd.to_datetime(
            df["last_claim"], unit="s"
        )
        df["days_since_last_claim"] = df["days_since_last_claim"].apply(
            lambda x: x.days if x.days > 0 else 1
        )
        df["avg_slp"] = df["in_game_slp"] / df["days_since_last_claim"]

        bad_scholars = df.loc[df["avg_slp"] < 100]

        bad_addresses = bad_scholars["index"].str.replace("0x", "ronin:")

        for address in bad_addresses:
            discord_id = scholar_info.loc[scholar_info["Address"] == address][
                "Scholar Discord ID"
            ].tolist()[0]
            manager = scholar_info.loc[scholar_info["Address"] == address][
                "Manager"
            ].tolist()[0]

            await self.send_warning(discord_id, manager)

    async def send_warning(self, discord_id, manager):

        # Code in alert.py
        manager = [user for user in self.bot.get_all_members() if user.name == manager][
            0
        ]

        # Scholar
        scholar = await self.bot.get_user(discord_id)

        e = discord.Embed(
            title="Low Average SLP Income",
            description=f"Hey {scholar.name}, we noticed that your average SLP income is below 100 SLP daily. If there is any reason why your SLP income is low, please contact your manager {manager.name} and explain your reasons.",
            color=0x00FFFF,
        )

        e.set_author(name="Axie Manager", icon_url=self.bot.user.avatar_url)

        e.set_footer(
            text="This is an automated message, if you believe this message was incorrectly send to you please notify your manager"
        )

        # Notify scholar and manager
        await scholar.send(embed=e)
        await manager.send(embed=e)

    @slp_warning.before_loop
    async def before_slp_warning(self):
        seconds = self.delta(14, 0, 1)
        await asyncio.sleep(seconds)

    @loop(hours=24)
    async def clean_listings(self):
        # Find discord channel
        channel = discord.utils.get(
            self.bot.get_all_channels(),
            guild__name="Axie Manager Scholar Group"
            if self.bot.user.id == 892855262124326932
            else "Bot Test Server",
            name="💎┃bot-alerts",
        )

        # Check if message is older than 24 hours
        # If it is, delete
        count = 0
        now = datetime.utcnow()
        history = await channel.history(limit=None).flatten()
        for msg in history:
            if msg.created_at <= now - timedelta(hours=24):
                await msg.delete()
                count += 1

        print(f"Removed {count} messages from 💎┃bot-alerts!")
        
    @loop(hours=4)
    async def leaderboard(self):
        """Print the current leaderboard in 🏆┃leaderboard channel
        """

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
        df = df[["name", "mmr", "in_game_slp", "last_claim"]]

        # Delete all the NaN values
        df = df.dropna()

        # Process the data
        df["name"] = df["name"].str.split("|").str[-1]
        df["last_claim"] = pd.to_datetime(df["last_claim"], unit="s")
        df["since_last_claim"] = (datetime.now() - df["last_claim"]).dt.days
        df.loc[df["since_last_claim"] < 1, "since_last_claim"] = 1
        df["avg_slp"] = df["in_game_slp"] / df["since_last_claim"]
        df = df.astype({"avg_slp": int})
        df = df.sort_values(by=["mmr", "avg_slp"], ascending=False)

        # Convert all columns to string
        df = df.astype(str)

        # Add emojis
        names = df["name"].tolist()
        names[0] = "🥇" + names[0]
        names[1] = "🥈" + names[1]
        names[2] = "🥉" + names[2]
        # names[-1] = '🤡' + names[-1]

        scholars = "\n".join(names)
        mmr = "\n".join(df["mmr"].tolist())
        avg_slp = "\n".join(df["avg_slp"].tolist())
        
        # Send message in discord channel
        channel = discord.utils.get(
            self.bot.get_all_channels(),
            guild__name="Axie Manager Scholar Group"
            if self.bot.user.id == 892855262124326932
            else "Bot Test Server",
            name="🏆┃leaderboard",
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

        await channel.send(embed=e)

def setup(bot):
    bot.add_cog(Tasks(bot))
