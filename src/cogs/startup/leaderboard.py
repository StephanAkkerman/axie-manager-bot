from datetime import datetime

import pandas as pd
import gspread
import gspread_dataframe as gd

import discord
from discord.ext import commands

from alerts.api import api_game_api

# Login using the .json file
gc = gspread.service_account(filename="authentication.json")

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    @commands.has_role("Scholar")
    async def leaderboard(self, ctx, message=None):
        
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
        df = df [['name', 'mmr', 'in_game_slp', 'last_claim']]

        # Process the data
        df['name'] = df['name'].str.split('|').str[-1]
        df['last_claim'] = pd.to_datetime(df['last_claim'],unit='s')
        df['since_last_claim'] = (datetime.now() - df['last_claim']).dt.days 
        df.loc[df['since_last_claim'] < 1, 'since_last_claim'] = 1
        df['avg_slp'] = df['in_game_slp'] / df['since_last_claim']
        df = df.astype({"avg_slp": int})
        df = df.sort_values(by=['mmr', 'avg_slp'], ascending=False)
        
        # Convert all columns to string
        df = df.astype(str)    
        
        # Add emojis
        names = df['name'].tolist()
        names[0] = '🥇' + names[0]
        names[1] = '🥈' + names[1]
        names[2] = '🥉' + names[2]
        #names[-1] = '🤡' + names[-1]
        
        scholars = "\n".join(names)
        mmr = "\n".join(df['mmr'].tolist())
        avg_slp = "\n".join(df['avg_slp'].tolist())
        
        e = discord.Embed(
                            title="Leaderboard",
                            description="",
                            color=0x00FFFF,
                        )

        e.add_field(
            name="Scholar",
            value= scholars,
            inline=True,
        )
        
        e.add_field(
            name="MMR",
            value= mmr,
            inline=True,
        )
        
        e.add_field(
            name="Average SLP",
            value= avg_slp,
            inline=True,
        )
        
        await ctx.channel.send(embed=e)
        
def setup(bot):
    bot.add_cog(Leaderboard(bot))
