##> Imports
# > Standard library
import json

# > 3rd party dependencies
import pandas as pd

# > Discord dependencies
import discord
from discord.ext import commands

# Local dependencies
from alerts.api import api_old_listings, api_axie_details
from config import config

class Price(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    async def get_axie_info(self, axie_id):
        df = await api_axie_details(axie_id)
        
        # Get all important info
        df["parts"] = [[d.get("id") for d in x] for x in df["parts"]]
        df["hp"] = pd.to_numeric(df["stats"].apply(lambda x: x["hp"]))
        df["morale"] = pd.to_numeric(df["stats"].apply(lambda x: x["morale"])).tolist()[0]
        df["speed"] = pd.to_numeric(df["stats"].apply(lambda x: x["speed"])).tolist()[0]
        df["skill"] = pd.to_numeric(df["stats"].apply(lambda x: x["skill"])).tolist()[0]                
        classes = json.dumps(df["class"].tolist()[0])
        parts1 = json.dumps(df["parts"][0][2:])
        parts2 = json.dumps(df["parts"][0])
                
        # Exact speed
        hp = [df["hp"].tolist()[0], df["hp"].tolist()[0]]
        speed = [df["speed"].tolist()[0], df["speed"].tolist()[0]]
        skill = [df["skill"].tolist()[0], df["skill"].tolist()[0]]
        morale = [df["morale"].tolist()[0], df["morale"].tolist()[0]]
        
        if int(df["breedCount"]) != 0:
            # This only works if it is not 0
            breedCount = list(range(int(df["breedCount"])))
        else:
            breedCount = [0]
       
        # 1st stage: breedcount, class, parts
        response1  = await api_old_listings(
            0,
            classes,
            breedCount,
            parts1,
            [27,61],
            [27,61],
            [27,61],
            [27,61],
        )
                        
        # Get price of this axie
        price1 = response1.head(1)['auction'].tolist()[0]['currentPriceUSD']
        id1 = response1.head(1)['id'].tolist()[0]
        
        # 2nd stage: +stats
        response2 = await api_old_listings(
            0,
            classes,
            breedCount,
            parts2,
            hp,
            speed,
            skill,
            morale,
        )
        
        price2 = response2.head(1)['auction'].tolist()[0]['currentPriceUSD']
        id2 = response2.head(1)['id'].tolist()[0]
        
        # 3rd stage: + r1
        
        # 4th stage: + r2
        
        return price1, id1, price2, id2 

    @commands.command(aliases=["prices"])
    @commands.has_role(config['ROLES']['SCHOLAR'])
    async def price(self, ctx, *input):
        """Request pricing advace using marketplace API

        Usage: `!price <axie_id>`
        Use this command to request information about good prices to sell your axie for.
        """
        if len(input) == 1:
            axie_id = input[0]
        else:
            raise commands.UserInputError()
        
        price1, id1, price2, id2 = await self.get_axie_info(axie_id)
        
        e = discord.Embed(title=f"Prices for axie #{axie_id}", description="", color=0x00FFFF, url=f"https://www.axieinfinity.com/axie/{axie_id}/")
        
        e.add_field(name="Class, Breedcount, Abilities", value=f"${price1} \nhttps://www.axieinfinity.com/axie/{id1}/", inline=False)
        e.add_field(name="+ Stats", value=f"${price2} \nhttps://www.axieinfinity.com/axie/{id2}/", inline=False)
        
        await ctx.send(embed=e)
    
def setup(bot):
    bot.add_cog(Price(bot))