##> Imports
# > Discord dependencies
import discord
from discord.ext import commands

# Import local dependencies
from config import config

class On_raw_reaction_add(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        
        # Ignore private messages
        if reaction.guild_id is None:
            return
        
        try:
            # Load necessary variables
            channel = self.bot.get_channel(reaction.channel_id)
            guild = self.bot.get_guild(reaction.guild_id)
            if reaction.user_id != self.bot.user.id:
                if channel.name == "👋┃welcome":
                    await self.verification_check(reaction, channel, guild)
                elif channel.name == "💎┃bot-alerts":
                    await self.claim_axie(reaction, channel)

        except commands.CommandError as e:
            exception_channel = self.bot.get_channel(reaction.channel_id)
            channel = discord.utils.get(guild.channels, name=config['ERROR'])
            await channel.send(
                f"Unhandled error in {exception_channel.mention}. User **{reaction.member.name}#{reaction.member.discriminator}** caused an error by adding a reaction to a message. ```{e}```"
            )

    async def verification_check(self, reaction, channel, guild):
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

    async def claim_axie(self, reaction, channel):
        msgs = [
            m
            for m in await channel.history(limit=None).flatten()
            if m.author == self.bot.user
        ]
        msg = None
        mention_msg = None

        for i in range(len(msgs)):
            if msgs[i].id == reaction.message_id:
                msg = msgs[i]
                if i <= len(msgs) - 1:
                    if msgs[i + 1].mentions:
                        mention_msg = msgs[i + 1]
                break

        # Check that the message is an embed, and the reaction is the gem stone emoji
        try:
            if len(msg.embeds) > 0 and str(reaction.emoji) == "\N{GEM STONE}":
                await reaction.member.send(embed=msg.embeds[0])
                await msg.delete()
                if mention_msg:
                    await mention_msg.delete()
        except AttributeError:
            pass


def setup(bot):
    bot.add_cog(On_raw_reaction_add(bot))
