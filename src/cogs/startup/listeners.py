import discord
from discord.ext import commands


class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener(name="on_command")
    async def print(self, ctx):
        print(f"{ctx.author} used !{ctx.command} in channel {ctx.message.channel}")

    ###################
    ###  REACTIONS  ###
    ###################

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        # Load necessary variables
        channel = self.bot.get_channel(reaction.channel_id)
        guild = self.bot.get_guild(reaction.guild_id)

        if (reaction.member.id != self.bot.user.id):
            if (channel.name == "👋┃welcome"):
                await self.verification_check(reaction, channel, guild)
            elif (channel.name == "💎┃bot-alerts"):
                await self.claim_axie(reaction, channel)

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
        msg = discord.utils.get(await channel.history(limit=None).flatten(), author=self.bot.user)

        # Check that the message is an embed, and the reaction is the gem stone emoji
        if (len(msg.embeds) > 0 and str(reaction.emoji) == "\N{GEM STONE}"):
            await reaction.member.send(embed=msg.embeds[0])
            await msg.delete()
            
    ###################
    # MEMBER  UPDATES #
    ###################

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if len(before.roles) < len(after.roles):
            await self.new_role(before, after)

    async def new_role(self, before, after):
        new_role = next(role for role in after.roles if role not in before.roles)
        if (new_role.name == "Tryout"):
            e = discord.Embed(
                title="Congratulations on passing the selection!",
                description=f"""Hello {after.mention},
                Congratulations on passing the selection! You will now be given the chance to compete for a limited scholarship!
                Here are the rules:
                - You will each be seperated in a group
                - You will then receive a time slot to play on the axie account
                - You can then play ONLY 10 games
                - After finishing 10 games please send us a screenshot and tell us you're done.

                Please note these important rules:
                - If you play more than 10 games YOU WILL BE INSTANTLY BANNED
                - if you play longer than your time frame YOU WILL BE INSTANTLY BANNED
                - if you do not update us once you are done with a screenshot YOU WILL BE INSTANTLY BANNED

                Best of luck!""",
                color=0x00FFFF,
            )
            e.set_author(name="Axie Manager")
            e.set_thumbnail(url=self.bot.user.avatar_url)
            e.set_footer("This is an automatically-generated message. Please do not reply here.")

            await after.send(embed=e)
            await after.send("https://youtu.be/2uG2lOfhe6s")

        elif (new_role.name == "Scholar"):
            e = discord.Embed(
                title="Congratulations on passing the selection!",
                description=f"""Hello {after.mention},
                Congratulations on passing the selection! You will now be given the chance to compete for a limited scholarship!
                Here are the rules:
                - You will each be seperated in a group
                - You will then receive a time slot to play on the axie account
                - You can then play ONLY 10 games
                - After finishing 10 games please send us a screenshot and tell us you're done.

                Please note these important rules:
                - If you play more than 10 games YOU WILL BE INSTANTLY BANNED
                - if you play longer than your time frame YOU WILL BE INSTANTLY BANNED
                - if you do not update us once you are done with a screenshot YOU WILL BE INSTANTLY BANNED

                Best of luck!""",
                color=0x00FFFF,
            )
            e.set_author(name="Axie Manager")
            e.set_thumbnail(url=self.bot.user.avatar_url)
            e.set_footer("This is an automatically-generated message. Please do not reply here.")

            await after.send(embed=e)
            await after.send("https://youtu.be/J2h_tOdMwoA")

def setup(bot):
    bot.add_cog(Listeners(bot))
