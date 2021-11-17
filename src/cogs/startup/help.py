import discord
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, *input):
        """Receive information about a command or list all commands

        Usage: `!help [command]`
        List all commands available to you. If you want more information about a specific command, simply type that command after `!help`.
        """
        # List all commands
        if not input:
            e = discord.Embed(
                title="Available commands",
                color=0x00FFFF,
                description="A list of available commands. Use `!help <command>` to get more information about a command!",
            )

            # Iterate through all commands
            for command in self.bot.walk_commands():
                # Check if user satisfies function checks (e.g. correct role)
                condition = True
                if condition:
                    for check in command.checks:
                        try:
                            check(ctx)
                        except commands.MissingRole:
                            condition = False
                            break
                    if condition:
                        aliases = command.name
                        for a in (alias for alias in command.aliases):
                            aliases += f" | {a}"
                        e.add_field(
                            name=aliases,
                            value=command.help.partition("\n")[0],
                            inline=False,
                        )
                else:
                    break

        # List the help for a specific command
        elif len(input) == 1:
            e = None
            for command in self.bot.walk_commands():
                # Check if user satisfies function checks (e.g. correct role)
                for check in command.checks:
                    try:
                        check(ctx)
                    except commands.MissingRole:
                        # Raise CommandNotFound, so users without permissions do not know that this command actually does exist.
                        raise commands.CommandNotFound()

                if (
                    command.name.lower() == input[0].lower()
                    or input[0].lower() in command.aliases
                ):
                    e = discord.Embed(title=f"{command} - Commands", color=0x00FFFF)
                    e.add_field(
                        name=f"!{command.name}", value=command.help, inline=False
                    )
                    break
            
            if (e == None):
                raise commands.CommandNotFound()

        # Too many arguments, give error message
        else:
            raise commands.UserInputError()

        e.set_author(name="Axie Manager")
        e.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=e)

    @help.error
    async def help_error(self, ctx, error):
        if(isinstance(error, commands.UserInputError)):
            await ctx.send(f"Too many arguments given. Correct usage of this command: `!help [command]`.")
        elif(isinstance(error, commands.CommandNotFound)):
            e = discord.Embed(
                title="Help",
                color=0x00FFFF,
                description="This command could not be found... Try `!help` to list all available commands.",
            )
            e.set_author(name="Axie Manager")
            e.set_thumbnail(url=self.bot.user.avatar_url)
            await ctx.send(embed=e)
        else:
            await ctx.send(
                f"Something went wrong when invoking the _{ctx.command.name}_ command... The managers have been notified of this problem."
            )
            channel = discord.utils.get(ctx.guild.channels, name="🐞┃bot-errors")
            await channel.send(
                f"Unhandled error in {ctx.message.channel.mention}. Exception caused by **{ctx.message.author.name}#{ctx.message.author.discriminator}** while invoking the _{ctx.command.name}_ command. \nUser message: `{ctx.message.content}` ```{error}```"
                )


def setup(bot):
    bot.add_cog(Help(bot))
