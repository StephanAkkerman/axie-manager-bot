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

class Instagram(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.instagram.start()
        
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
        timestamp = datetime.utcfromtimestamp(last_post['taken_at_timestamp'])
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
            old_description = last_message.embeds[0].to_dict()["description"]
        except Exception:
            old_description = None

        # Do nothing
        if old_description == caption:
            return

        e = discord.Embed(
            title=f"New Instagram post published on {timestamp}",
            description=caption,
            url=post_url,
            color=0x00FFFF,
        )

        e.set_image(url=img_url)
        e.set_footer(text=f"❤️ {likes} | 💬 {comments}")
        e.set_author(name=username, icon_url=profile_pic, url=acc_url)

        await channel.send(embed=e)


def setup(bot):
    bot.add_cog(Instagram(bot))