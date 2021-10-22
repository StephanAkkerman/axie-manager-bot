from datetime import datetime, timedelta

import discord
from discord.ext import commands
from discord.ext.tasks import loop


class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.clean_listings.start()

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
