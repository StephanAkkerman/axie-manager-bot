import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, *input):
        """ Receive information about a command or list all commands
        
        """
        # List all commands
        if not input: 
            e = discord.Embed(title="Available commands", color=0x00ffff, description="A list of available commands. Use `!help <command>` to get more information about a command!", )
            
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
                        e.add_field(name=f'!{command.name}', value=command.help.partition('\n')[0], inline=False)
                else:
                    break

        # List the help for a specific command
        elif (len(input) == 1):
            for command in self.bot.walk_commands():
                # Check if user satisfies function checks (e.g. correct role)
                for check in command.checks:
                    try:
                        check(ctx)
                    except commands.MissingRole:
                        raise
                if (command.name.lower() == input[0].lower()):
                    e = discord.Embed(title=f'{command} - Commands', color=0x00ffff)
                    e.add_field(name=f'!{command.name}', value=command.help, inline=False)
                    break

        # Too many arguments, give error message
        else:
            raise
        
        e.set_author(name="Axie Manager")
        e.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=e)

    @help.error
    async def help_error(self,ctx,error):
        e = discord.Embed(title="Help", color=0x00ffff, description="This command could not be found... Try `!help` to list all available commands.")
        e.set_author(name="Axie Manager")
        e.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=e)

def setup(bot):
    bot.add_cog(Help(bot))
