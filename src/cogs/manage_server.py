import discord
from discord.ext import commands

class ManageServer(commands.Cog):    
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    #@commands.has_role("Manager")
    async def announce(self, ctx, *input):
        """ Make an announcement to a channel
        
        """
        # Confirm command used
        create_msg = await ctx.send(f'Creating announcement in channel {input[0]}... What should the announcement be?')

        # Await announcement body
        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author and message.channel == ctx.channel)
        split_msg = msg.content.split('\n', 1)        

        # Create Discord embed from msg
        e = discord.Embed(title=split_msg[0], description="" if len(split_msg) == 1 else split_msg[1], color=0x00ffff)
        
        e.add_field(name='Channel', value=input[0], inline=False)
        e.set_author(name="Axie Manager")
        e.set_thumbnail(url=self.bot.user.avatar_url)
        e.set_footer(text='This is a preview. Please confirm that all info is correct. Channel field will not be visible in the final message.')
        
        # Send preview announcement
        preview_msg = await ctx.send(embed=e)
        await preview_msg.add_reaction('\N{WHITE HEAVY CHECK MARK}')
        await preview_msg.add_reaction('\N{CROSS MARK}')

        # Handle preview accept/deny using reactions
        reaction = await self.bot.wait_for('reaction_add', check=lambda r,u: (str(r.emoji) == '\N{WHITE HEAVY CHECK MARK}' or str(r.emoji) == '\N{CROSS MARK}') and u == ctx.author)

        if (reaction[0].emoji == '\N{WHITE HEAVY CHECK MARK}'):
            e.remove_field(index=0)
            e.set_footer(text="This is an official announcement by the Axie Managers")
            channel = discord.utils.get(self.bot.get_all_channels(), id=int(input[0][2:-1]))
            await ctx.send(f'Anouncement made in {input[0]}!')
            await channel.send(embed=e)
        elif(reaction[0].emoji == '\N{CROSS MARK}'):
            await create_msg.delete()
            await preview_msg.delete()
            await ctx.send(f'Make a new announcement using `!announce <channel>` and follow the instructions.')

    @announce.error
    async def announce_error(self,ctx,error):
        if isinstance(error, commands.MissingRole):
            await ctx.message.author.send(f'Sorry, you do not have permission to use this command. Please contact a manager if you think that you should.')
        

def setup(bot):
    bot.add_cog(ManageServer(bot))
