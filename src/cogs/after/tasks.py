import asyncio
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

import discord
from discord.ext import commands
from discord.ext.tasks import loop

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
