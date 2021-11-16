from datetime import datetime, timedelta

import pandas as pd
import gspread
import gspread_dataframe as gd

import discord
from discord.ext import commands

# Login using the .json file
gc = gspread.service_account(filename="authentication.json")

from alerts.api import api_game_api_single

class ScholarData(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    @commands.has_role("Scholar")
    async def mydata(self, ctx, message=None):
        
        # Delete this message, to remove clutter
        await ctx.message.delete()
        
        # Open Scholars spreadsheet
        ws = gc.open("Scholars").worksheet("Scholars")
        scholar_info = (
            gd.get_as_dataframe(ws).dropna(axis=0, how="all").dropna(axis=1, how="all")
        )
        
        address = scholar_info.loc[scholar_info['Scholar Discord ID'] == ctx.message.author.id]['Address']

        if not address.empty:
            df = await api_game_api_single(address.tolist()[0])
            
            # Process data in df
            df['cache_last_updated'] = pd.to_datetime(df['cache_last_updated'],unit='ms').dt.strftime('Updated on: %Y-%m-%d, %H:%M:%S UTC (+8h for PHT)')
            
            e = discord.Embed(
                                title="Your in-game data",
                                description="",
                                color=0x00FFFF,
                            )
            
            e.set_author(name="Axie Manager", icon_url=self.bot.user.avatar_url)
            e.set_thumbnail(url=self.bot.user.avatar_url)
            e.add_field(
                name="In-game SLP",
                value= str(df['in_game_slp'].tolist()[0]),
                inline=False,
            )
            
            e.add_field(
                name="MMR",
                value= df['mmr'].tolist()[0],
                inline=False,
            )
            
            e.add_field(
                name="Rank",
                value= df['rank'].tolist()[0],
                inline=False,
            )
            
            payout_date = (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=14)
            
            e.add_field(
                name="Next Payout Date",
                value= payout_date.strftime("%Y-%m-%d"),
                inline=False,
            )
            
            e.add_field(
                name="Days Until Next Payout",
                value= str((payout_date - datetime.now()).days),
                inline=False,
            )
            
            e.set_footer(
                            text=df['cache_last_updated'].tolist()[0]
                        )
            
            await ctx.message.author.send(embed=e)
            
        else:
            print("This user didn't receive their personal data : " + ctx.message.author.name)
            print("Discord ID : " + str(ctx.message.author.id))
            print("Current time : ", datetime.now().strftime("%H:%M:%S"))
            
            await ctx.message.author.send(
                    "Sorry, something went wrong when trying to load your personal data. Please contact a manager."
                )
        
def setup(bot):
    bot.add_cog(ScholarData(bot))