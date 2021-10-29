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

        role = discord.utils.find(
            lambda r: r.name in ["Akkie100", "BreakDownzPvp", "MrJuggler", "unheil", "Joepermans", "ManDerMannen"],
            ctx.author.roles
        )
        mgr = discord.utils.find(
            lambda m: m.name == role.name and "Manager" in [n.name for n in m.roles],
            ctx.guild.members
        )
        
        await ctx.reply(f"Your manager is **{mgr.display_name}**! If you want to ask them something, please message them _privately_.")

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
