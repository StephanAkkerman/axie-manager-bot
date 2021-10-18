from itertools import islice

import discord
from discord.ext import commands

class ManageServer(commands.Cog):    
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role("Manager")
    async def announce(self, ctx, *input):
        """ Make an announcement to a channel
        
            Usage: `!announce <channel>`
            Link the channel as the first argument. After this, the bot will ask you what message you want to relay to that channel.
            The first line is the title of the announcement. Everything after that will be put in the body.
            Confirm or deny using the emoji reactions.
        """

        if (len(input) == 0 or len(input) > 1):
            await ctx.send('Incorrect usage. Use `!announce <channel>`. For more help, see `!help announce`.')
            return

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

    ###################
    ### NEW COMMAND ###
    ###################

    @commands.command()
    @commands.has_role("Manager")
    async def clear(self, ctx, *input):
        """ Clear an amount of messages from a user (if specified)

            Usage: `!clear <amount> [user]`
            Specify the amount of messages you want to delete. If you want to delete a certain amount of messages by a specific user,
            also specify the user by adding @<username>.
        """

        # Clear x amount of messages from channel
        if (len(input) == 1):
            await ctx.channel.purge(limit=int(input[0]) + 1)

        # Clear x amount of messages from user from channel
        elif (len(input) == 2):
            user = self.bot.get_user(int(input[1][3:-1]))
            msgs = []
            counter = 0
            async for message in ctx.channel.history(limit=None):
                if message.author == user:
                    if (counter < int(input[0])):
                        msgs.append(message)
                        counter += 1
                    else:
                        break

            await ctx.channel.delete_messages(msgs)

        else:
            raise

    @clear.error
    async def clear_error(self,ctx,error):
        if isinstance(error, commands.MissingRole):
            await ctx.message.author.send(f'Sorry, you do not have permission to use this command. Please contact a manager if you think that you should.')
        else:
            await ctx.send(f'This command was not used correctly. Please see `!help clear` for a more detailed explanation on how to use this command.')

    ###################
    ### NEW COMMAND ###
    ###################

    @commands.command()
    @commands.has_role("Manager")
    async def mute(self, ctx, *input):
        """ Assign the '[mute]' role to a user

            Usage: `!mute <user>`
            Specify to which user you want to assign the [mute] role. This only works when your server has a role named '[mute]' exactly!
        """
        # Add role [mute] to mentioned user
        if (len(input) == 1):
            user = ctx.guild.get_member(int(input[0][3:-1]))
            role = discord.utils.get(ctx.guild.roles, name='[mute]')
            await user.add_roles(role)
        else:
            raise
    
    @mute.error
    async def mute_error(self,ctx,error):
        print(error)
        if isinstance(error, commands.MissingRole):
            await ctx.message.author.send(f'Sorry, you do not have permission to use this command. Please contact a manager if you think that you should.')
        else:
            await ctx.send(f'This command was not used correctly or the role "[mute]" does not exist. Please see `!help mute` for a more detailed explanation on how to use this command.')


def setup(bot):
    bot.add_cog(ManageServer(bot))
