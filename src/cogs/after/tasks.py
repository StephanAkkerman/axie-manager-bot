import asyncio
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
import gspread
import gspread_dataframe as gd
import pandas as pd

import discord
from discord.ext import commands
from discord.ext.tasks import loop

from alerts.api import 

gc = gspread.service_account(filename="authentication.json")
class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.clean_listings.start()
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
            gd.get_as_dataframe(gc.open("Scholars").worksheet("Scholars")).dropna(axis=0, how="all").dropna(axis=1, how="all")
        )

        # Get all addresses and join together as a string seperated by commas
        together = ",".join(scholar_info["Address"].tolist())

        # Call all addresses at once and retreive json
        response = requests.get(
            "https://game-api.axie.technology/api/v1/" + together
        ).json()

        df = pd.DataFrame(response).transpose().reset_index()

        df['days_since_last_claim'] = (datetime.now() - pd.to_datetime(df['last_claim'],unit='s'))
        df['days_since_last_claim'] = df['days_since_last_claim'].apply(lambda x: x.days if x.days > 0 else 1)
        df['avg_slp'] = df['in_game_slp'] / df['days_since_last_claim']

        bad_scholars = df.loc[df['avg_slp'] < 100]

        bad_addresses = bad_scholars['index'].str.replace('0x', 'ronin:')

        for address in bad_addresses:
            discord_id = scholar_info.loc[scholar_info['Address'] == address]['Scholar Discord ID'].tolist()[0]
            
            await send_warning(discord_id)
            
    async def send_warning(discord_id):
        pass

    @slp_warning.before_loop
    async def before_slp_warning(self):
        seconds = self.delta(14,0,1)
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


def setup(bot):
    bot.add_cog(Tasks(bot))
