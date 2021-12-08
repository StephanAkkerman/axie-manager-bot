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


class Slp_warning(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Start loops
        self.slp_warning.start()

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

def setup(bot):
    bot.add_cog(Slp_warning(bot))
