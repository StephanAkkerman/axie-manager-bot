##> Imports
import sys

# 3rd party imports
import aiohttp
from tenacity import retry, stop_after_attempt, wait_fixed
import pandas as pd

# > Discord dependencies
import discord
from discord.ext import commands
from discord.ext.tasks import loop

# > Local dependencies
from config import config
from alerts.graphql import *
from alerts.api import api_axie_details

class Prices(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.prices.start()
        
    async def get_prices(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                'https://api.binance.com/api/v3/ticker/price'
            ) as r:
                response = await r.json()
                return response
            
    
    @retry(stop=stop_after_attempt(12), wait=wait_fixed(5))
    async def get_floor_price(self):
        """Gets the old listings on the market and returns it as a pandas dataframe"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json={
                    "query": old_axies_query,
                    "operationName": old_axie_operationName,
                    "variables": """{
                        "from": 0,
                        "size": 1,
                        "sort": "PriceAsc",
                        "auctionType": "Sale",
                        "criteria": {"stages":[4]}
                        }"""
                },
            ) as r:
                response = await r.json()
                floor_id = response['data']['axies']['results'][0]['id']
                
                # Get this axie's auction info
                floor_df = await api_axie_details(floor_id)
                return float(floor_df['auction'].tolist()[0]['currentPriceUSD']), floor_id

    @loop(hours=4)
    async def prices(self):
        
        binance_prices = await self.get_prices()
        price_df = pd.DataFrame(binance_prices)
        
        # Get SLP and AXS 
        slp = float(price_df.loc[price_df['symbol'] == 'SLPUSDT']['price'].tolist()[0])
        axs = float(price_df.loc[price_df['symbol'] == 'AXSUSDT']['price'].tolist()[0])
        
        # Get floor price
        floor_price, floor_id = await self.get_floor_price()
        
        # Get channel for price updates
        channel = discord.utils.get(
            self.bot.get_all_channels(),
            guild__name=config["DEBUG"]["GUILD_NAME"]
            if len(sys.argv) > 1 and sys.argv[1] == "-test"
            else config["DISCORD"]["GUILD_NAME"],
            name=config["LOOPS"]["PRICES"]["CHANNEL"],
        )
        
        e = discord.Embed(
            title="Price overview",
            description="",
            url = f"https://marketplace.axieinfinity.com/axie/{floor_id}/",
            color=0x00FFFF,
        )
        
        guild = discord.utils.get(
            self.bot.guilds,
            name=config["DEBUG"]["GUILD_NAME"]
            if len(sys.argv) > 1 and sys.argv[1] == "-test"
            else config["DISCORD"]["GUILD_NAME"],
        )
        
        slp_emoji = discord.utils.get(guild.emojis, name=config['EMOJIS']['SLP'])
        axs_emoji = discord.utils.get(guild.emojis, name=config['EMOJIS']['AXS'])
        
        e.add_field(
            name=f"SLP {slp_emoji}", value=f"${round(slp,4)}", inline=False,
        )
        e.add_field(
            name=f"AXS {axs_emoji}", value=f"${round(axs,3)}", inline=False,
        )
        e.add_field(
            name="Floor price", value=f"${round(floor_price,2)}", inline=False,
        )
        
        await channel.send(embed=e)
    
def setup(bot):
    bot.add_cog(Prices(bot))