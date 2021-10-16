from discord.ext import commands

class Listeners(commands.Cog):    
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener(name='on_command')
    async def print(self, ctx):
        print(f'{ctx.author} used !{ctx.command} in channel {ctx.message.channel}')

def setup(bot):
    bot.add_cog(Listeners(bot))
