##> Imports
# > Standard library
import json

# > 3rd party dependencies
import pandas as pd

# > Discord dependencies
import discord
from discord.ext import commands

# Local dependencies
from alerts.api import api_old_listings, api_axie_details, api_genes
from config import config

class Price(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    async def get_axie_info(self, axie_id):
        
        # Get all the info
        classes, parts1, parts2, breedCount, hp, speed, skill, morale = await self.formatted_axie_info(axie_id)
       
        # 1st stage: breedcount, class, parts
        response1 = await self.get_first_price(classes, breedCount, parts1)
        try:
            price1 = response1.head(1)['auction'].tolist()[0]['currentPriceUSD']
            id1 = response1.head(1)['id'].tolist()[0]
        except Exception:
            return 0, 0, 0, 0, 0, 0, 0, 0
        
        # 2nd stage: +stats
        response2 = await self.get_second_price(0, classes, breedCount, parts2, hp, speed, skill, morale)
        try:
            price2 = response2.head(1)['auction'].tolist()[0]['currentPriceUSD']
            id2 = response2.head(1)['id'].tolist()[0]
        except Exception:
            return price1, id1, 0, 0, 0, 0, 0, 0
        
        # Get this axie's genes
        axie_genes = await self.get_axie_genes(axie_id)
                        
        # Search for perfect R1 and R2, using same data from response2
        genes = await self.get_axie_genes(",".join(response2['id'].tolist()))
            
        # 3rd stage: + r1 (abilities)
        response3 = self.r1_abilities(axie_genes, genes)
        
        start = 0
        while response3.empty and not genes.empty:
            start += 100
            response2 = await self.get_second_price(start, classes, breedCount, parts2, hp, speed, skill, morale)
            genes = await self.get_axie_genes(",".join(response2['id'].tolist()))
            response3 = self.r1_abilities(axie_genes, genes)
        
        try:
            # Get matching id from the response
            id3 = response3.head(1)['story_id'].tolist()[0]
            
            # Lookup this id in response2
            response3_axie = response2.loc[response2['id'] == id3]
            price3 = response3_axie['auction'].tolist()[0]['currentPriceUSD']

        except Exception:
            return price1, id1, price2, id2, 0, 0, 0, 0
        
        # 4th stage: + r1 (all)
        # Reset local vars
        start = 0
        response2 = await self.get_second_price(start, classes, breedCount, parts2, hp, speed, skill, morale)
        genes = await self.get_axie_genes(",".join(response2['id'].tolist()))
        response4 = self.r1_all(axie_genes, genes)
        
        while response4.empty and not genes.empty:
            start += 100
            response2 = await self.get_second_price(start, classes, breedCount, parts2, hp, speed, skill, morale)
            genes = await self.get_axie_genes(",".join(response2['id'].tolist()))
            response4 = self.r1_all(axie_genes, genes)
            
        
        try:
            # Get matching id from the response
            id4 = response4.head(1)['story_id'].tolist()[0]
            
            # Lookup this id in response2
            response4_axie = response2.loc[response2['id'] == id4]
            price4 = response4_axie['auction'].tolist()[0]['currentPriceUSD']
            
        except Exception:
            return price1, id1, price2, id2, price3, id3, 0, 0
        
        return price1, id1, price2, id2, price3, id3, price4, id4
    
    def r1_abilities(self, axie_genes, genes):
        
        return genes.loc[(genes["mouth r1"] == (axie_genes["mouth r1"].tolist()[0])) &
                         (genes["horn r1"] == (axie_genes["horn r1"].tolist()[0])) &
                         (genes["back r1"] ==(axie_genes["back r1"].tolist()[0])) &
                         (genes["tail r1"] == (axie_genes["tail r1"].tolist()[0])) 
                         ]
    
    def r1_all(self, axie_genes, genes):
        
        return genes.loc[(genes["eyes r1"] == (axie_genes["eyes r1"].tolist()[0])) & 
                         (genes["ears r1"] == (axie_genes["ears r1"].tolist()[0])) & 
                         (genes["mouth r1"] == (axie_genes["mouth r1"].tolist()[0])) &
                         (genes["horn r1"] == (axie_genes["horn r1"].tolist()[0])) &
                         (genes["back r1"] ==(axie_genes["back r1"].tolist()[0])) &
                         (genes["tail r1"] == (axie_genes["tail r1"].tolist()[0])) 
                         ]
        
    
    async def formatted_axie_info(self, axie_id):
        
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
            
        return classes, parts1, parts2, breedCount, hp, speed, skill, morale
    
    async def get_first_price(self, classes, breedCount, parts1):
        try:
            return await api_old_listings(
                0,
                classes,
                breedCount,
                parts1,
                [27,61],
                [27,61],
                [27,61],
                [27,61],
            )
        except Exception:
            return pd.DataFrame({})
            
    async def get_second_price(self, start, classes, breedCount, parts2, hp, speed, skill, morale):
        
        try:
            return await api_old_listings(
                start,
                classes,
                breedCount,
                parts2,
                hp,
                speed,
                skill,
                morale,
            )     
        except Exception:
            return pd.DataFrame({})
        
    async def get_axie_genes(self, axie_id):
        
        # ['cls', 'region', 'pattern', 'color', 'eyes', 'mouth', 'ears', 'horn', 'back', 'tail', 'axieId']
        response = await api_genes(axie_id)
                                   
        if type(response) == dict:
            genes = pd.DataFrame.from_dict(response, orient="index").transpose()
        else:
            if response == None:
                return pd.DataFrame({})
            else:
                genes = pd.DataFrame([pd.Series(value) for value in response])
        
        # Remove nan ids
        genes = genes[genes["story_id"].notna()]
        
        # Add columns for parts
        for part in ["eyes", "ears", "mouth", "horn", "back", "tail"]:
            try:
                genes[f"{part} r1"] = genes["traits"].apply(lambda x: x[part]["r1"]['partId'])
                genes[f"{part} r2"] = genes["traits"].apply(lambda x: x[part]["r2"]['partId'])
            except Exception as e:
                print(e)
                print(",".join(genes["story_id"].to_list()))
                
        return genes

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
        
        price1, id1, price2, id2, price3, id3, price4, id4 = await self.get_axie_info(axie_id)
        
        e = discord.Embed(title=f"Prices for axie #{axie_id}", description="", color=0x00FFFF, url=f"https://www.axieinfinity.com/axie/{axie_id}/")
        
        if id1 != 0:
            e.add_field(name="Class, Breedcount, Abilities", value=f"${price1} \nhttps://www.axieinfinity.com/axie/{id1}/", inline=False)
        if id2 != 0:
            e.add_field(name="+ Stats", value=f"${price2} \nhttps://www.axieinfinity.com/axie/{id2}/", inline=False)
        if id3 != 0:
            e.add_field(name="+ R1 (abilities)", value=f"${price3} \nhttps://www.axieinfinity.com/axie/{id3}/", inline=False)
        if id4 != 0:
            e.add_field(name="+ R1 (all)", value=f"${price4} \nhttps://www.axieinfinity.com/axie/{id4}/", inline=False)
        
        await ctx.send(embed=e)
    
def setup(bot):
    bot.add_cog(Price(bot))