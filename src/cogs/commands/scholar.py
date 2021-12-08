##> Imports
# > 3rd Party Dependencies
import discord
from discord.ext import commands
import pandas as pd
import numpy as np
import gspread
import gspread_dataframe as gd

# Login using the .json file
gc = gspread.service_account(filename="authentication.json")


class Scholar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role("Manager")
    async def scholar(self, ctx, *input):
        """Add a scholar

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
                    scholar_info["Scholar Discord ID"] = (
                        scholar_info["Scholar Discord ID"].astype(np.int64).astype(str)
                    )

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
    bot.add_cog(Scholar(bot))
