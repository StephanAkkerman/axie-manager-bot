##> Imports
# > Standard libraries
import asyncio
from datetime import datetime, timedelta

# > 3rd party dependencies
from dateutil.relativedelta import relativedelta
import gspread
import gspread_dataframe as gd
import pandas as pd
import aiohttp

# > Discord dependencies
import discord
from discord.ext import commands
from discord.ext.tasks import loop

# > Local dependencies
from alerts.api import api_game_api

gc = gspread.service_account(filename="authentication.json")


class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Start loops
        self.clean_listings.start()
        self.slp_warning.start()
        
    def delta(self, day, hour, minute):
        """Calculate the amount of seconds until the next day, hour, minute triple"""
        now = datetime.now()
        future = datetime(now.year, now.month, day, hour, minute)

        if now.day >= day:
            future += relativedelta(months=+1)
        elif now.hour >= hour and now.minute > minute:
            future += timedelta(days=1)

        return (future - now).seconds + (future - now).days * 24 * 3600

    @loop(hours=168)
    async def slp_warning(self):
        scholar_info = (
            gd.get_as_dataframe(gc.open("Scholars").worksheet("Scholars"))
            .dropna(axis=0, how="all")
            .dropna(axis=1, how="all")
        )

        # Get all addresses and join together as a string seperated by commas
        together = ",".join(scholar_info["Address"].tolist())

        # Call all addresses at once and retreive json
        df = api_game_api(together).reset_index()

        df["days_since_last_claim"] = datetime.now() - pd.to_datetime(
            df["last_claim"], unit="s"
        )
        df["days_since_last_claim"] = df["days_since_last_claim"].apply(
            lambda x: x.days if x.days > 0 else 1
        )
        df["avg_slp"] = df["in_game_slp"] / df["days_since_last_claim"]

        bad_scholars = df.loc[df["avg_slp"] < 100]

        bad_addresses = bad_scholars["index"].str.replace("0x", "ronin:")

        for address in bad_addresses:
            discord_id = scholar_info.loc[scholar_info["Address"] == address][
                "Scholar Discord ID"
            ].tolist()[0]
            manager = scholar_info.loc[scholar_info["Address"] == address][
                "Manager"
            ].tolist()[0]

            await self.send_warning(discord_id, manager)

    async def send_warning(self, discord_id, manager):

        # Code in alert.py
        manager = [user for user in self.bot.get_all_members() if user.name == manager][
            0
        ]

        # Scholar
        scholar = await self.bot.get_user(discord_id)

        e = discord.Embed(
            title="Low Average SLP Income",
            description=f"Hey {scholar.name}, we noticed that your average SLP income is below 100 SLP daily. If there is any reason why your SLP income is low, please contact your manager {manager.name} and explain your reasons.",
            color=0x00FFFF,
        )

        e.set_author(name="Axie Manager", icon_url=self.bot.user.avatar_url)

        e.set_footer(
            text="This is an automated message, if you believe this message was incorrectly send to you please notify your manager"
        )

        # Notify scholar and manager
        await scholar.send(embed=e)
        await manager.send(embed=e)

    @slp_warning.before_loop
    async def before_slp_warning(self):
        seconds = self.delta(14, 0, 1)
        await asyncio.sleep(seconds)

    @loop(hours=24)
    async def clean_listings(self):
        # Find discord channel
        channel = discord.utils.get(
            self.bot.get_all_channels(),
            guild__name="Axie Manager Scholar Group"
            if self.bot.user.id == 892855262124326932
            else "Bot Test Server",
            name="💎┃bot-alerts",
        )

        # Check if message is older than 24 hours
        # If it is, delete
        count = 0
        now = datetime.utcnow()
        history = await channel.history(limit=None).flatten()
        for msg in history:
            if msg.created_at <= now - timedelta(hours=24):
                await msg.delete()
                count += 1

        print(f"Removed {count} messages from 💎┃bot-alerts!")

    async def get_last_post(self):
        headers = {
            "Host": "www.instagram.com",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 "
            "Safari/537.11 ",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://www.instagram.com/" + "Axie_Manager" + "/feed/?__a=1",
                headers=headers,
            ) as r:
                response = await r.json()
                return response["graphql"]["user"]["edge_owner_to_timeline_media"][
                    "edges"
                ][0]["node"]

    @loop(hours=6)
    async def instagram(self):
        """Checks if a new instagram posts has been uploaded
        If a new post is available it will be posted in the social media channel
        """

        last_post = await self.get_last_post()

        # Set variables
        img_url = last_post["display_url"]
        caption = last_post["edge_media_to_caption"]["edges"][0]["node"]["text"]
        comments = last_post["edge_media_to_comment"]["count"]
        likes = last_post["edge_liked_by"]["count"]
        # timestamp = datetime.utcfromtimestamp(last_post['taken_at_timestamp'])
        post_url = "https://www.instagram.com/" + "p/" + last_post["shortcode"]

        # Profile data
        username = last_post["owner"]["username"]
        acc_url = "https://www.instagram.com/" + username
        # Could use server pic url instead, this is not saved in last_post :(
        profile_pic = "https://scontent-amt2-1.cdninstagram.com/v/t51.2885-19/s150x150/242140939_1247428002403281_8571533909443045803_n.jpg?_nc_ht=scontent-amt2-1.cdninstagram.com&_nc_cat=109&_nc_ohc=PS1zXEwOE50AX_s3MAI&edm=ALbqBD0BAAAA&ccb=7-4&oh=ec01133a8f3188ee7abdcb35411e8015&oe=61A802AB&_nc_sid=9a90d6"

        # Send message in discord channel
        channel = discord.utils.get(
            self.bot.get_all_channels(),
            guild__name="Axie Manager Scholar Group"
            if self.bot.user.id == 892855262124326932
            else "Bot Test Server",
            name="💗┃social-media",
        )

        # Last message sent by the bot
        last_message = await channel.history().find(
            lambda m: m.author.id == self.bot.user.id
        )

        try:
            old_img_url = last_message.embeds[0].to_dict()["image"]["url"]
        except Exception:
            old_img_url = None

        # Do nothing
        if old_img_url == img_url:
            return

        e = discord.Embed(
            title="New Instagram Post",
            description=caption,
            url=post_url,
            color=0x00FFFF,
        )

        e.set_image(url=img_url)
        e.set_footer(text=f"❤️ {likes} | 💬 {comments}")
        e.set_author(name=username, icon_url=profile_pic, url=acc_url)

        await channel.send(embed=e)


def setup(bot):
    bot.add_cog(Tasks(bot))
