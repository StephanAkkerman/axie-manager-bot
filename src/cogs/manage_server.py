from random import randrange
import math

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

        channel = discord.utils.get(
                self.bot.get_all_channels(), id=int(input[0][2:-1])
            )

        if (channel == None):
            raise

        # Confirm command used
        create_msg = await ctx.send(
            f"Creating announcement in channel {input[0]}... What should the announcement be?"
        )

        # Await announcement body
        msg = await self.bot.wait_for(
            "message",
            check=lambda message: message.author == ctx.author
            and message.channel == ctx.channel,
        )
        split_msg = msg.content.split("\n", 1)

        # Create Discord embed from msg
        e = discord.Embed(
            title=split_msg[0],
            description="" if len(split_msg) == 1 else split_msg[1],
            color=0x00FFFF,
        )

        e.add_field(name="Channel", value=input[0], inline=False)
        e.set_author(name="Axie Manager")
        e.set_thumbnail(url=self.bot.user.avatar_url)
        e.set_footer(
            text="This is a preview. Please confirm that all info is correct. Channel field will not be visible in the final message."
        )

        # Send preview announcement
        preview_msg = await ctx.send(embed=e)
        await preview_msg.add_reaction("\N{WHITE HEAVY CHECK MARK}")
        await preview_msg.add_reaction("\N{CROSS MARK}")

        # Handle preview accept/deny using reactions
        reaction = await self.bot.wait_for(
            "reaction_add",
            check=lambda r, u: (
                str(r.emoji) == "\N{WHITE HEAVY CHECK MARK}"
                or str(r.emoji) == "\N{CROSS MARK}"
            )
            and u == ctx.author,
        )

        if reaction[0].emoji == "\N{WHITE HEAVY CHECK MARK}":
            e.remove_field(index=0)
            e.set_footer(text="This is an official announcement by the Axie Managers")
            await ctx.send(f"Anouncement made in {input[0]}!")
            await channel.send(embed=e)
        elif reaction[0].emoji == "\N{CROSS MARK}":
            await create_msg.delete()
            await preview_msg.delete()
            await ctx.send(
                f"Make a new announcement using `!announce <channel>` and follow the instructions."
            )

    @announce.error
    async def announce_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.message.author.send(
                f"Sorry, you do not have permission to use this command. Please contact a manager if you think that you should."
            )
        else:
            await ctx.send(
                "Incorrect usage. Use `!announce <channel>`. For more help, see `!help announce`."
            )

    ###################
    ### NEW COMMAND ###
    ###################

    @commands.command()
    @commands.has_role("Manager")
    async def clear(self, ctx, *input):
        """ Clear an amount of messages [from a user if specified]

            Usage: `!clear <amount> [user]`
            Specify the amount of messages you want to delete. If you want to delete a certain amount of messages by a specific user,
            also specify the user by adding @<username>.
        """

        # Clear x amount of messages from channel
        if len(input) == 1:
            await ctx.channel.purge(limit=int(input[0]) + 1)

        # Clear x amount of messages from user from channel
        elif len(input) == 2:
            user = self.bot.get_user(int(input[1][3:-1]))
            msgs = []
            counter = 0
            async for message in ctx.channel.history(limit=None):
                if message.author == user:
                    if counter < int(input[0]):
                        msgs.append(message)
                        counter += 1
                    else:
                        break

            await ctx.channel.delete_messages(msgs)

        else:
            raise

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.message.author.send(
                f"Sorry, you do not have permission to use this command. Please contact a manager if you think that you should."
            )
        else:
            await ctx.send(
                f"This command was not used correctly. Please see `!help clear` for a more detailed explanation on how to use this command."
            )

    ###################
    ### NEW COMMAND ###
    ###################

    @commands.command()
    @commands.has_role("Manager")
    async def mute(self, ctx, *input):
        """ Assign the '[mute]' role to a user

            Usage: `!mute <user>`
            Specify to which user you want to assign the '[mute]' role. This only works when your server has a role named '[mute]' exactly! 
            The '[mute]' role should be listed above the role of the mentioned user and the assigned bot role should be listed above the user's.
            To unmute a user, use `!unmute <user>`. For more info, see `!help unmute`.
        """
        # Add role [mute] to mentioned user
        if len(input) == 1:
            user_id = int(input[0][3:-1]) if '!' in input[0] else int(input[0][2:-1])
            user = ctx.guild.get_member(user_id)
            role = discord.utils.get(ctx.guild.roles, name="[mute]")
            await user.add_roles(role)
            await ctx.send(f"User **{user.display_name}** has been muted.")
        else:
            raise

    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.message.author.send(
                f"Sorry, you do not have permission to use this command. Please contact a manager if you think that you should."
            )
        else:
            await ctx.send(
                f'This command was not used correctly or the role "[mute]" does not exist. Please see `!help mute` for a more detailed explanation on how to use this command.'
            )

    ###################
    ### NEW COMMAND ###
    ###################

    @commands.command()
    @commands.has_role("Manager")
    async def unmute(self, ctx, *input):
        """ Remove the '[mute]' role from a user

            Usage: `!unmute <user>`
            Specify from which user you want to remove the [mute] role.
        """
        # Remove role [mute] from mentioned user
        if len(input) == 1:
            user = ctx.guild.get_member(int(input[0][3:-1]))
            role = discord.utils.get(ctx.guild.roles, name="[mute]")
            await user.remove_roles(role)
            await ctx.send(f"User **{user.display_name}** has been unmuted.")
        else:
            raise

    @unmute.error
    async def unmute_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.message.author.send(
                f"Sorry, you do not have permission to use this command. Please contact a manager if you think that you should."
            )
        else:
            await ctx.send(
                f'This command was not used correctly or the role "[mute]" does not exist. Please see `!help unmute` for a more detailed explanation on how to use this command.'
            )

    ###################
    ### NEW COMMAND ###
    ###################

    @commands.command()
    @commands.has_role("Manager")
    async def tryout(self, ctx, *input):
        """ Start tryouts
        
            Usage: `!tryout [number of groups]`
            Specify the number of tryout groups. If no argument given, all tryout groups will be used. Bot will ask for tryout settings confirmation.
            After confirmation tryouts will start.
        """
        if len(input) <= 1:
            # Get everyone that has the "Tryout" role
            role = discord.utils.get(ctx.guild.roles, name="Tryout")
            tryouts = role.members

            # Place tryouts in roles at random
            roles = [r for r in ctx.guild.roles if r.name.startswith("Group")]
            roles.reverse()

            # Decide the amount of tryouts per group
            group_amount = len(roles) if len(input) == 0 else int(input[0])
            group_size = math.ceil(len(tryouts) / group_amount)
            groups = roles[:group_amount]

            # Assign role to tryout
            tryouts_dict = {}
            for group in groups:
                tryouts_dict[group] = []

            for tryout in tryouts:
                # Continue until succesful
                while 1:
                    group = randrange(group_amount)
                    if len(tryouts_dict[groups[group]]) + 1 <= group_size:
                        tryouts_dict[groups[group]].append(tryout)
                        break

            # Ask for confirmation
            e = discord.Embed(title="Confirm Tryout", description="", color=0x00FFFF)
            e.add_field(name="No. tryouts", value=len(tryouts), inline=True)
            e.add_field(name="Amount of groups", value=group_amount, inline=True)
            e.add_field(name="Max no. tryouts per group", value=group_size, inline=True)

            # Add all tryouts to correct group in confirmation
            for k, v in tryouts_dict.items():
                value = ""
                for tryout in v:
                    value += f"{tryout.name}\n"

                e.add_field(name=k.name, value=value, inline=True)

            e.set_author(name="Axie Manager")
            e.set_thumbnail(url=self.bot.user.avatar_url)
            e.set_footer(text="Confirm that these are the correct tryout settings.")

            # Send confirmation request
            confirm_msg = await ctx.send(embed=e)
            await confirm_msg.add_reaction("\N{WHITE HEAVY CHECK MARK}")
            await confirm_msg.add_reaction("\N{CROSS MARK}")

            # Handle preview accept/deny using reactions
            reaction = await self.bot.wait_for(
                "reaction_add",
                check=lambda r, u: (
                    str(r.emoji) == "\N{WHITE HEAVY CHECK MARK}"
                    or str(r.emoji) == "\N{CROSS MARK}"
                )
                and u == ctx.author,
            )

            if reaction[0].emoji == "\N{WHITE HEAVY CHECK MARK}":
                # Add tryouts to roles
                for k, v in tryouts_dict.items():
                    for tryout in v:
                        await tryout.add_roles(k)
                await ctx.send(f"**STARTING TRYOUTS!**")

            # Cancel tryouts
            elif reaction[0].emoji == "\N{CROSS MARK}":
                await confirm_msg.delete()
                await ctx.send(
                    f"Cancelled tryouts. To start a tryout use `!tryout [number of groups]` or see `!help tryout`."
                )

        else:
            raise

    @tryout.error
    async def tryout_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.message.author.send(
                f"Sorry, you do not have permission to use this command. Please contact a manager if you think that you should."
            )
        else:
            await ctx.send(
                f"Something went wrong... For information on how to use this function, see `!help tryout`"
            )


def setup(bot):
    bot.add_cog(ManageServer(bot))