##> Imports
# > Standard library
from datetime import datetime

# > 3rd party dependencies
import pandas as pd
import gspread
import gspread_dataframe as gd

# > Discord dependencies
import discord
from discord.ext import commands

# > Local dependencies
from alerts.api import api_game_api

# Login using the .json file
gc = gspread.service_account(filename="authentication.json")

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    @commands.has_role("Scholar")
    async def leaderboard(self, ctx):
        """Print the current leaderboard

        Usage: `!leaderboard`
        Print the best performing scholars.
        """

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
        
    @leaderboard.error
    async def leaderboard_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.send(f"You do not have permissions to use this command. If you think that you should, please contact a manager.")
        else:
            await ctx.send(
                f"Something went wrong when invoking the _{ctx.command.name}_ command... The managers have been notified of this problem."
            )
            channel = discord.utils.get(ctx.guild.channels, name="🐞┃bot-errors")
            await channel.send(
                f"Unhandled error in {ctx.message.channel.mention}. Exception caused by **{ctx.message.author.name}#{ctx.message.author.discriminator}** while invoking the _{ctx.command.name}_ command. \nUser message: `{ctx.message.content}` ```{error}```"
            )


def setup(bot):
    bot.add_cog(Leaderboard(bot))
