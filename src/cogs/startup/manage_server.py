##> Imports
# > Standard library
from random import randrange
import math
import datetime

# > 3rd Party Dependencies
import discord
from discord.ext import commands
import pandas as pd
import numpy as np
import gspread
import gspread_dataframe as gd

# Login using the .json file
gc = gspread.service_account(filename="authentication.json")


class ManageServer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role("Manager")
    async def announce(self, ctx, *input):
        """Make an announcement to a channel

        Usage: `!announce <channel>`
        Link the channel as the first argument. After this, the bot will ask you what message you want to relay to that channel.
        The first line is the title of the announcement. Everything after that will be put in the body.
        Confirm or deny using the emoji reactions.
        """

        if len(input) == 0:
            raise commands.UserInputError()

        try:
            channel = discord.utils.get(
                self.bot.get_all_channels(), id=int(input[0][2:-1])
            )
        except:
            raise commands.ChannelNotFound(input[0][2:-1])

        if not channel:
            raise commands.ChannelNotFound(input[0][2:-1])

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
            e.timestamp = datetime.datetime.utcnow()
            e.set_footer(text="This is an official announcement by the Axie Managers")
            await create_msg.delete()
            await msg.delete()
            await ctx.send(f"Anouncement made in {input[0]}!")
            await channel.send(embed=e)
        elif reaction[0].emoji == "\N{CROSS MARK}":
            await create_msg.delete()
            await msg.delete()
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
        elif isinstance(error, commands.ChannelNotFound):
            await ctx.send(
                f"Sorry, the supplied channel could not be found. Try again or see `!help announce` for more information."
            )
        elif isinstance(error, commands.UserInputError):
            await ctx.send(
                f"Sorry, you used this command incorrectly. Correct usage is `!announce <channel>`. Try again or see `!help announce` for more information."
            )
        else:
            await ctx.send(
                f"Something went wrong when invoking the _{ctx.command.name}_ command... The managers have been notified of this problem."
            )
            channel = discord.utils.get(ctx.guild.channels, name="🐞┃bot-errors")
            await channel.send(
                f"Unhandled error in {ctx.message.channel.mention}. Exception caused by **{ctx.message.author.name}#{ctx.message.author.discriminator}** while invoking the _{ctx.command.name}_ command. \nUser message: `{ctx.message.content}` ```{error}```"
            )

    ###################
    ### NEW COMMAND ###
    ###################

    @commands.command(aliases=["purge", "remove", "delete"])
    @commands.has_role("Manager")
    async def clear(self, ctx, *input):
        """Clear an amount of messages [from a user if specified]

        Usage: `!clear <amount> [user]`
        Specify the amount of messages you want to delete. If you want to delete a certain amount of messages by a specific user,
        also specify the user by adding @<username>.
        """
        # Clear x amount of messages from channel
        if len(input) == 1:
            try:
                await ctx.channel.purge(limit=int(input[0]) + 1)
            except:
                raise commands.UserInputError()

        # Clear x amount of messages from user from channel
        elif len(input) == 2:
            try:
                user = self.bot.get_user(int(input[1][3:-1]))
            except:
                raise commands.UserNotFound(input[1][3:-1])

            if not user:
                raise commands.UserNotFound(input[1][3:-1])

            msgs = []
            counter = 0
            async for message in ctx.channel.history(limit=None):
                if message.author == user:
                    try:
                        int(input[0])
                    except:
                        raise commands.UserInputError()
                    if counter < int(input[0]):
                        msgs.append(message)
                        counter += 1
                    else:
                        break

            await ctx.channel.delete_messages(msgs)

        else:
            raise commands.UserInputError()

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.message.author.send(
                f"Sorry, you do not have permission to use this command. Please contact a manager if you think that you should."
            )
        elif isinstance(error, commands.UserNotFound):
            await ctx.send(
                f"Sorry, this user could not be found. To find a user, you must mention them. Try again or see `!help clear` for more information."
            )
        elif isinstance(error, commands.UserInputError):
            await ctx.send(
                f"Sorry, you used this command incorrectly. Correct usage is `!clear <amount> [user]`. Try again or see `!help clear` for more information."
            )
        else:
            await ctx.send(
                f"Something went wrong when invoking the _{ctx.command.name}_ command... The managers have been notified of this problem."
            )
            channel = discord.utils.get(ctx.guild.channels, name="🐞┃bot-errors")
            await channel.send(
                f"Unhandled error in {ctx.message.channel.mention}. Exception caused by **{ctx.message.author.name}#{ctx.message.author.discriminator}** while invoking the _{ctx.command.name}_ command. \nUser message: `{ctx.message.content}` ```{error}```"
            )

    ###################
    ### NEW COMMAND ###
    ###################

    @commands.command()
    @commands.has_role("Manager")
    async def mute(self, ctx, *input):
        """Assign the '[mute]' role to a user

        Usage: `!mute <user>`
        Specify to which user you want to assign the '[mute]' role. This only works when your server has a role named '[mute]' exactly!
        The '[mute]' role should be listed above the role of the mentioned user and the assigned bot role should be listed above the user's.
        To unmute a user, use `!unmute <user>`. For more info, see `!help unmute`.
        """
        # Add role [mute] to mentioned user
        if len(input) == 1:
            try:
                user_id = (
                    int(input[0][3:-1]) if "!" in input[0] else int(input[0][2:-1])
                )
            except:
                raise commands.UserNotFound("")

            try:
                user = ctx.guild.get_member(user_id)
            except:
                raise commands.UserNotFound(user_id)

            if not user:
                raise commands.UserNotFound(user_id)

            role = discord.utils.get(ctx.guild.roles, name="[mute]")
            await user.add_roles(role)
            await ctx.send(f"User **{user.display_name}** has been muted.")
        else:
            raise commands.UserInputError()

    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.message.author.send(
                f"Sorry, you do not have permission to use this command. Please contact a manager if you think that you should."
            )
        elif isinstance(error, commands.UserNotFound):
            await ctx.send(
                f"Sorry, this user could not be found. To find a user, you must mention them. Try again or see `!help mute` for more information."
            )
        elif isinstance(error, commands.UserInputError):
            await ctx.send(
                f"Sorry, you used this command incorrectly. Correct usage is `!mute <user>`. Try again or see `!help mute` for more information."
            )
        else:
            await ctx.send(
                f"Something went wrong when invoking the _{ctx.command.name}_ command... The managers have been notified of this problem."
            )
            channel = discord.utils.get(ctx.guild.channels, name="🐞┃bot-errors")
            await channel.send(
                f"Unhandled error in {ctx.message.channel.mention}. Exception caused by **{ctx.message.author.name}#{ctx.message.author.discriminator}** while invoking the _{ctx.command.name}_ command. \nUser message: `{ctx.message.content}` ```{error}```"
            )

    ###################
    ### NEW COMMAND ###
    ###################

    @commands.command()
    @commands.has_role("Manager")
    async def unmute(self, ctx, *input):
        """Remove the '[mute]' role from a user

        Usage: `!unmute <user>`
        Specify from which user you want to remove the [mute] role.
        """
        # Remove role [mute] from mentioned user
        if len(input) == 1:
            try:
                user_id = (
                    int(input[0][3:-1]) if "!" in input[0] else int(input[0][2:-1])
                )
            except:
                raise commands.UserNotFound("")

            try:
                user = ctx.guild.get_member(user_id)
            except:
                raise commands.UserNotFound(user_id)

            role = discord.utils.get(ctx.guild.roles, name="[mute]")
            await user.remove_roles(role)
            await ctx.send(f"User **{user.display_name}** has been unmuted.")
        else:
            raise commands.UserInputError()

    @unmute.error
    async def unmute_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.message.author.send(
                f"Sorry, you do not have permission to use this command. Please contact a manager if you think that you should."
            )
        elif isinstance(error, commands.UserNotFound):
            await ctx.send(
                f"Sorry, this user could not be found. To find a user, you must mention them. Try again or see `!help unmute` for more information."
            )
        elif isinstance(error, commands.UserInputError):
            await ctx.send(
                f"Sorry, you used this command incorrectly. Correct usage is `!unmute <user>`. Try again or see `!help unmute` for more information."
            )
        else:
            await ctx.send(
                f"Something went wrong when invoking the _{ctx.command.name}_ command... The managers have been notified of this problem."
            )
            channel = discord.utils.get(ctx.guild.channels, name="🐞┃bot-errors")
            await channel.send(
                f"Unhandled error in {ctx.message.channel.mention}. Exception caused by **{ctx.message.author.name}#{ctx.message.author.discriminator}** while invoking the _{ctx.command.name}_ command. \nUser message: `{ctx.message.content}` ```{error}```"
            )

    ###################
    ### NEW COMMAND ###
    ###################

    @commands.command(aliases=["tryouts"])
    @commands.has_role("Manager")
    async def tryout(self, ctx, *input):
        """Start tryouts

        Usage: `!tryout [number of groups|stop|end]`
        Specify the number of tryout groups. If no argument given, all tryout groups will be used. Bot will ask for tryout settings confirmation.
        After confirmation tryouts will start.
        Use "stop" or "end" as first argument to end tryouts.
        """
        if len(input) <= 1:
            if len(input) == 1 and (
                input[0].lower() == "stop" or input[0].lower() == "end"
            ):
                # Get everyone that has the "Tryout" role
                role = discord.utils.get(ctx.guild.roles, name="Tryout")
                tryouts = role.members

                for tryout in tryouts:
                    roles = [r for r in tryout.roles if r.name.startswith("Group")]
                    if len(roles) > 0:
                        await tryout.remove_roles(*roles)

                await ctx.send("**TRYOUTS ENDED!**")

            else:
                # Get everyone that has the "Tryout" role
                role = discord.utils.get(ctx.guild.roles, name="Tryout")
                tryouts = role.members

                # Place tryouts in roles at random
                roles = [r for r in ctx.guild.roles if r.name.startswith("Group")]
                roles.reverse()

                # Decide the amount of tryouts per group
                try:
                    group_amount = len(roles) if len(input) == 0 else int(input[0])
                except:
                    raise commands.UserInputError()
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
                e = discord.Embed(
                    title="Confirm Tryout", description="", color=0x00FFFF
                )
                e.add_field(name="No. tryouts", value=len(tryouts), inline=True)
                e.add_field(name="Amount of groups", value=group_amount, inline=True)
                e.add_field(
                    name="Max no. tryouts per group", value=group_size, inline=True
                )

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
            raise commands.UserInputError()

    @tryout.error
    async def tryout_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.message.author.send(
                f"Sorry, you do not have permission to use this command. Please contact a manager if you think that you should."
            )
        elif isinstance(error, commands.UserInputError):
            await ctx.send(
                f"Sorry, you used this command incorrectly. Correct usage is `!tryout [number of groups|stop/end]`. Try again or see `!help tryout` for more information."
            )
        else:
            await ctx.send(
                f"Something went wrong when invoking the _{ctx.command.name}_ command... The managers have been notified of this problem."
            )
            channel = discord.utils.get(ctx.guild.channels, name="🐞┃bot-errors")
            await channel.send(
                f"Unhandled error in {ctx.message.channel.mention}. Exception caused by **{ctx.message.author.name}#{ctx.message.author.discriminator}** while invoking the _{ctx.command.name}_ command. \nUser message: `{ctx.message.content}` ```{error}```"
            )

    ###################
    ### NEW COMMAND ###
    ###################

    @commands.command()
    @commands.has_role("Manager")
    async def scholar(self, ctx, *input):
        """ Add a scholar 
        
        Usage: `!scholar <scholar_discord_id> <address> <split> <payout_address> <encrypted_key> <[manager]>`
        This will add the specified scholar to the Scholars Google spreadsheet.       
        """

        if len(input) >= 5:
            new_scholar = discord.utils.get(ctx.guild.members, id=int(input[0]))

            if "Verified" in [r.name for r in new_scholar.roles]:
                # Get managers info
                try:
                    manager_ids = [
                        int(id[3:-1]) if "!" in id else int(id[2:-1])
                        for id in list(input[5:])
                    ]
                except:
                    raise commands.MemberNotFound(
                        (id[3:-1]) if "!" in id else int(id[2:-1])
                        for id in list(input[5:])
                    )

                if not manager_ids:
                    raise commands.MemberNotFound(
                        (id[3:-1]) if "!" in id else int(id[2:-1])
                        for id in list(input[5:])
                    )

                managers = [m for m in ctx.guild.members if m.id in manager_ids]

                # Ask for confirmation
                e = discord.Embed(
                    title="Confirm New Scholar", description="", color=0x00FFFF
                )
                e.add_field(name="Scholar Name", value=new_scholar.name, inline=True)
                e.add_field(
                    name="Scholar Discord ID", value=new_scholar.id, inline=True
                )
                e.add_field(
                    name="Scholar Share", value=f"{float(input[2])*100}%", inline=True
                )
                e.add_field(name="Address", value=input[1], inline=True)
                e.add_field(name="Payout Address", value=input[3], inline=True)
                e.add_field(name="Encrypted key", value=input[4], inline=True)
                e.add_field(
                    name="Manager(s)",
                    value="\n".join(manager.display_name for manager in managers),
                    inline=True,
                )
                e.set_author(name="Axie Manager")
                e.set_thumbnail(url=self.bot.user.avatar_url)
                e.set_footer(
                    text="Confirm that this is the correct info to add a new scholar."
                )

                confirm_msg = await ctx.send(embed=e)
                await confirm_msg.add_reaction("\N{WHITE HEAVY CHECK MARK}")
                await confirm_msg.add_reaction("\N{CROSS MARK}")

                # Handle confirmation using reactions
                reaction = await self.bot.wait_for(
                    "reaction_add",
                    check=lambda r, u: (
                        str(r.emoji) == "\N{WHITE HEAVY CHECK MARK}"
                        or str(r.emoji) == "\N{CROSS MARK}"
                    )
                    and u == ctx.author,
                )

                if reaction[0].emoji == "\N{WHITE HEAVY CHECK MARK}":
                    # Add the "Scholar" role
                    scholar_role = discord.utils.get(ctx.guild.roles, name="Scholar")
                    await new_scholar.add_roles(scholar_role)

                    # Add the manager roles
                    manager_roles = [
                        r
                        for r in ctx.guild.roles
                        if r.name in [m.display_name for m in managers]
                    ]
                    [await new_scholar.add_roles(r) for r in manager_roles]

                    # Send a DM to this new scholars manager(s)
                    e.title = "You are now managing a new scholar!"
                    e.set_footer(text=discord.Embed.Empty)
                    [await manager.send(embed=e) for manager in managers]

                    # Send a DM to the new scholar
                    await new_scholar.send(
                        f"Your manager{' is**' if len(managers) == 1 else 's are**'} {' and '.join([m.display_name for m in managers])}**! If you want to ask them something, please message them _privately_."
                    )

                    await ctx.send(
                        f"Succesfully added **{new_scholar.display_name}** as a scholar!"
                    )

                    # Convert accepted information to a dataframe
                    new_scholar = pd.DataFrame(
                        {
                            "Scholar Name": new_scholar.name,
                            "Manager": "\n".join(
                                manager.display_name for manager in managers
                            ),
                            "Scholar Share": input[2],
                            "Address": input[1],
                            "Payout Address": input[3],
                            "Scholar Discord ID": str(new_scholar.id),
                            "Info": input[4],
                        },
                        index=[0],
                    )

                    # Add scholar to google spreadsheets
                    # Read current Scholars spreadsheet
                    ws = gc.open("Scholars").worksheet("Scholars")

                    # Get it as an df
                    scholar_info = (
                        gd.get_as_dataframe(ws)
                        .dropna(axis=0, how="all")
                        .dropna(axis=1, how="all")
                    )
                    
                    # Append the info to it
                    scholar_info = scholar_info.append(new_scholar)
                    
                    # Convert to int64 and then to string
                    scholar_info["Scholar Discord ID"] = scholar_info["Scholar Discord ID"].astype(np.int64).astype(str)

                    # Upload it
                    gd.set_with_dataframe(ws, scholar_info, include_index=False)

                elif reaction[0].emoji == "\N{CROSS MARK}":
                    await confirm_msg.delete()
                    await ctx.send(
                        f"Cancelled addition of new scholar. To add a new scholar, use `!scholar <scholar> <address> <split> <payout_address> <[manager]>` or see `!help scholar`."
                    )

            else:
                raise commands.UserNotFound(input[0])

        else:
            raise commands.UserInputError()

    @scholar.error
    async def scholar_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.message.author.send(
                f"Sorry, you do not have permission to use this command. Please contact a manager if you think that you should."
            )
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(
                f"Sorry, could not find the supplied manager(s). Did you mention them?"
            )
        elif isinstance(error, commands.UserNotFound):
            await ctx.send(
                f"Sorry, the new scholar is not yet verified. Ask them to verify themselves first."
            )
        elif isinstance(error, commands.UserInputError):
            await ctx.send(
                f"Sorry, you used this command incorrectly. Correct usage is `!scholar <scholar_discord_id> <address> <split> <payout_address> <encrypted_key> <[manager]>`. Try again or see `!help scholar` for more information."
            )
        else:
            await ctx.send(
                f"Something went wrong when invoking the _{ctx.command.name}_ command... The managers have been notified of this problem."
            )
            channel = discord.utils.get(ctx.guild.channels, name="🐞┃bot-errors")
            await channel.send(
                f"Unhandled error in {ctx.message.channel.mention}. Exception caused by **{ctx.message.author.name}#{ctx.message.author.discriminator}** while invoking the _{ctx.command.name}_ command. \nUser message: `{ctx.message.content}` ```{error}```"
            )


def setup(bot):
    bot.add_cog(ManageServer(bot))
