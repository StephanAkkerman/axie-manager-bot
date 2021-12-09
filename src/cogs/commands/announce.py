##> Imports
# > Standard library
import datetime

# > 3rd Party Dependencies
import discord
from discord.ext import commands

# Local dependencies
from config import config

class Announce(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role(config['ROLES']['MANAGER'])
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
        e.set_author(name=config['MANAGER_NAME'])
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
            channel = discord.utils.get(ctx.guild.channels, name=config['ERROR']['CHANNEL'])
            await channel.send(
                f"Unhandled error in {ctx.message.channel.mention}. Exception caused by **{ctx.message.author.name}#{ctx.message.author.discriminator}** while invoking the _{ctx.command.name}_ command. \nUser message: `{ctx.message.content}` ```{error}```"
            )
            
def setup(bot):
    bot.add_cog(Announce(bot))