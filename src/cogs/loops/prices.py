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
from alerts.api import api_genes


class Prices(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.prices.start()

    async def get_prices(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.binance.com/api/v3/ticker/price") as r:
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
                        "size": 30,
                        "sort": "PriceAsc",
                        "auctionType": "Sale",
                        "criteria": {"stages":[4]}
                        }""",
                },
            ) as r:
                response = await r.json()
                df = pd.DataFrame(response["data"]["axies"]["results"])

                # Get prices
                df["price"] = pd.to_numeric(
                    df["auction"].apply(lambda x: x["currentPriceUSD"])
                )

                # Average over the currentPriceUSD
                avg_floor = df["price"].mean()

                return avg_floor

    @loop(hours=4)
    async def prices(self):

        binance_prices = await self.get_prices()
        price_df = pd.DataFrame(binance_prices)

        # Get SLP and AXS
        slp = float(price_df.loc[price_df["symbol"] == "SLPUSDT"]["price"].tolist()[0])
        axs = float(price_df.loc[price_df["symbol"] == "AXSUSDT"]["price"].tolist()[0])
        eth = float(price_df.loc[price_df["symbol"] == "ETHUSDT"]["price"].tolist()[0])

        # Get floor price
        #floor_price = await self.get_floor_price()

        # Get channel for price updates
        channel = discord.utils.get(
            self.bot.get_all_channels(),
            guild__name=config["DEBUG"]["GUILD_NAME"]
            if len(sys.argv) > 1 and sys.argv[1] == "-test"
            else config["DISCORD"]["GUILD_NAME"],
            name=config["LOOPS"]["PRICES"]["CHANNEL"],
        )

        e = discord.Embed(
            title="",
            description="",
            color=0x00FFFF,
        )

        guild = discord.utils.get(
            self.bot.guilds,
            name=config["DEBUG"]["GUILD_NAME"]
            if len(sys.argv) > 1 and sys.argv[1] == "-test"
            else config["DISCORD"]["GUILD_NAME"],
        )

        slp_emoji = discord.utils.get(guild.emojis, name=config["EMOJIS"]["SLP"])
        axs_emoji = discord.utils.get(guild.emojis, name=config["EMOJIS"]["AXS"])
        eth_emoji = discord.utils.get(guild.emojis, name=config["EMOJIS"]["ETH"])

        e.add_field(
            name=f"SLP {slp_emoji}",
            value=f"${round(slp,4)}",
            inline=False,
        )
        e.add_field(
            name=f"AXS {axs_emoji}",
            value=f"${round(axs,3)}",
            inline=False,
        )
        e.add_field(
            name=f"ETH {eth_emoji}",
            value=f"${round(eth,3)}",
            inline=False,
        )
        #e.add_field(
        #    name="Mean Floor Price",
        #    value=f"${round(floor_price,2)}",
        #    inline=False,
        #)

        await channel.send(embed=e)


def setup(bot):
    bot.add_cog(Prices(bot))
