##> Imports
# > Standard libraries
from datetime import datetime, timedelta
import sys

# > Discord dependencies
import discord
from discord.ext import commands
from discord.ext.tasks import loop

# Local dependencies
from config import config
class Clean_channel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Start loops
        self.clean_channel.start()

    @loop(hours=config["LOOPS"]["CLEAN_CHANNEL"]["HOURS"])
    async def clean_channel(self):
        
        # Find discord channel
        channel = discord.utils.get(
            self.bot.get_all_channels(),
            guild__name=config["DEBUG"]["GUILD_NAME"]
            if len(sys.argv) > 1 and sys.argv[1] == "-test"
            else config["DISCORD"]["GUILD_NAME"],
            name=config["LOOPS"]["CLEAN_CHANNEL"]["CHANNEL"],
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
    bot.add_cog(Clean_channel(bot))
