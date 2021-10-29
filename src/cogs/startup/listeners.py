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

        if reaction.member.id != self.bot.user.id:
            if channel.name == "👋┃welcome":
                await self.verification_check(reaction, channel, guild)
            elif channel.name == "💎┃bot-alerts":
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
        msgs = [m for m in await channel.history(limit=None).flatten() if m.author==self.bot.user]
        msg = None

        for m in msgs:
            if m.id == reaction.message_id:
                msg = m

        # Check that the message is an embed, and the reaction is the gem stone emoji
        if len(msg.embeds) > 0 and str(reaction.emoji) == "\N{GEM STONE}":
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
                You have been chosen🌟 
                Congratulations on passing our tryout selection! Now you will get the chance to prove your skills to win an exciting scholarship program at Axie Manager!

                Here is some important information before you get started on your exciting journey with us!ℹ️ 

                - If you are ever lost in our discord refer to the 🔑 Information category to find how to navigate our discord
                - Please visit 📆  | welcome-tryouts to get started with the tryout process!
                - In the 🙇‍♂️  tryout category you will find all the tryout related topics! A perfect place to seek advice or socialize with your fellow tryouts!
                - If you ever get lose the login don't worry we got you. Simply type: !qr in the 🤖┃login channel to get your qr!

                Before you get started please watch the following video as this video will explain the entire tryout process!

                Show us what you got and best of luck🍀 
                _You play to earn and we will manage the rest😎_""",
                color=0x00FFFF,
            )
            e.set_author(name="Axie Manager")
            e.set_thumbnail(url=self.bot.user.avatar_url)
            e.set_footer(text="This is an automatically-generated message. Please do not reply to this message.")

            await after.send(embed=e)
            await after.send("https://youtu.be/2uG2lOfhe6s")

        elif (new_role.name == "Scholar"):
            e = discord.Embed(
                title="Congratulations on becoming a scholar!",
                description=f"""Hello {after.mention},
                A Big Congratulations! 🎊 
                We are thrilled to have you on board as a scholar of our fast growing Axie Infinity group! 
                Here at Axie Manager we seek the best players for a scholarship where you play to earn 💰 and we manage the rest 😎 

                Here is some important information before you get started on your exciting journey with us!ℹ️ 
                - If you are ever lost in our discord refer to the 🔑 Information category to find how to navigate our discord
                - In the 🎓  scholar category you will find all the scholar related topics! A perfect place to seek advice or discuss meta strats with your fellow scholars!
                - If you ever get lose the login don't worry we got you. Simply type: !qr in the 🤖┃login channel to get your qr!

                To summarize we have created a simple video for you!

                Thank you for joining our Axie Infinity group, now let's get that juicy SLP🤑""",
                color=0x00FFFF,
            )
            e.set_author(name="Axie Manager")
            e.set_thumbnail(url=self.bot.user.avatar_url)
            e.set_footer(text="This is an automatically-generated message. Please do not reply to this message.")

            await after.send(embed=e)
            await after.send("https://youtu.be/J2h_tOdMwoA")

def setup(bot):
    bot.add_cog(Listeners(bot))
