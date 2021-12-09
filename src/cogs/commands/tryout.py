##> Imports
# > Standard library
from random import randrange
import math

# > 3rd Party Dependencies
import discord
from discord.ext import commands

# Local dependencies
from config import config

class Tryout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
    
    @commands.command(aliases=["tryouts"])
    @commands.has_role(config['ROLES']['MANAGER'])
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
            channel = discord.utils.get(ctx.guild.channels, name=config['ERROR']['CHANNEL'])
            await channel.send(
                f"Unhandled error in {ctx.message.channel.mention}. Exception caused by **{ctx.message.author.name}#{ctx.message.author.discriminator}** while invoking the _{ctx.command.name}_ command. \nUser message: `{ctx.message.content}` ```{error}```"
            )
            
def setup(bot):
    bot.add_cog(Tryout(bot))
