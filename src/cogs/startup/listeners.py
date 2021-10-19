import discord
from discord.ext import commands


class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener(name="on_command")
    async def print(self, ctx):
        print(f"{ctx.author} used !{ctx.command} in channel {ctx.message.channel}")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        # Load necessary variables
        channel = self.bot.get_channel(reaction.channel_id)
        guild = self.bot.get_guild(reaction.guild_id)
        original_msg = (await channel.history(oldest_first=True, limit=1).flatten())[0]
        role = discord.utils.get(guild.roles, name="Verified")

        # Check if this is the original verification message
        if reaction.message_id == original_msg.id:
            if str(reaction.emoji) == "\N{WHITE HEAVY CHECK MARK}":
                await reaction.member.add_roles(role)
                print(f'{reaction.member.display_name} just got the role "{role.name}"')
            else:
                r = discord.utils.get(original_msg.reactions, emoji=reaction.emoji.name)
                await r.remove(reaction.member)


def setup(bot):
    bot.add_cog(Listeners(bot))
