import discord
from discord.ext import commands


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role("Scholar")
    async def manager(self, ctx):
        """ Find out who your manager is
        
        Usage: `!manager`
        With this command you can find out who your manager is! Please, do not message them in this channel but send a DM.
        """
        
        roles = [r.name for r in ctx.author.roles if r.name in ["Akkie100", "BreakDownzPvp", "MrJuggler", "unheil", "Joepermans", "ManDerMannen"]]
        managers = [m.display_name for m in ctx.guild.members if m.name in roles and "Manager" in [r.name for r in m.roles]]
        managernames = " and ".join(managers)

        await ctx.reply(f"Your manager{' is**' if len(managers) == 1 else 's are**'} {managernames}**! If you want to ask them something, please message them _privately_.")

    @manager.error
    async def manager_error(self,ctx,error):
        if isinstance(error, commands.MissingRole):
            await ctx.reply(
                f"Sorry, you do not have permission to use this command. Please contact a manager if you think that you should."
            )
        else:
            await ctx.send(
                f"Something went wrong... Have you checked that you have a managers name as a role?"
            )



def setup(bot):
    bot.add_cog(Misc(bot))
