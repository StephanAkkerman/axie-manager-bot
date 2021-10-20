# Standard libraries
import json
import traceback
import asyncio
from datetime import datetime

# Discord imports
import discord
from discord.ext import commands

# 3rd party dependencies
import pandas as pd  # For parsing data
from urllib.request import urlopen
from PIL import Image
from io import BytesIO
import aiohttp

# Local files
from alerts.graphql import *
from alerts.builds import get_builds
from alerts.genes import get_genes


class Alert(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.send = []
        self.specifications = get_builds()

        # Start functions
        self.bot.loop.create_task(self.new_listings())
        self.bot.loop.create_task(self.old_listings())

    async def send_alert(self, axie_df, build=None):
        """
        Takes an axie dataframe and build and sends a message in the discord channel for each of them
        """

        if not axie_df.empty:
            for _, row in axie_df.iterrows():
                if row["id"] not in self.send:
                    link = (
                        "https://marketplace.axieinfinity.com/axie/" + row["id"] + "/"
                    )

                    # Send message in discord channel
                    channel = discord.utils.get(
                        self.bot.get_all_channels(),
                        guild__name="Axie Manager Scholar Group" if self.bot.user.id == 892855262124326932 else "Bot Test Server",
                        name="💎┃bot-alerts",
                    )

                    e = discord.Embed(
                        title=build["Name"],
                        description="",
                        url=link,
                        color=0x00FFFF,
                    )
                    
                    e.set_author(name="Axie Manager", icon_url=self.bot.user.avatar_url)

                    e.add_field(name='Current Price', value=f"${str(row['auction'])}\n", inline=True)
                    e.add_field(name='Starting price', value=f"Ξ{round(int(row['auction_info']['startingPrice']) * 0.000000000000000001, 2)}\n", inline=True)
                    e.add_field(name='Ending price', value=f"Ξ{round(int(row['auction_info']['endingPrice']) * 0.000000000000000001, 2)}\n", inline=True)
                    
                    e.add_field(name=':eggplant:', value=str(row['breedCount']), inline=True)
                    e.add_field(name='Class', value=row['class'], inline=True)
                    [e.add_field(name=stat[1:-5].capitalize(), value=stat[-2:], inline=True) for stat in str(row['stats'])[1:-28].split(", ")]

                    d = ""
                    r1 = ""
                    r2 = ""
                    for part in ['eyes', 'ears', "mouth", "horn", "back", "tail"]:
                        d += f"{(row[part]['d']['name'])}\n"
                        r1 += f"{(row[part]['r1']['name'])}\n"
                        r2 += f"{(row[part]['r2']['name'])}\n"

                    e.add_field(name="D", value=d, inline=True)
                    e.add_field(name="R1", value=r1, inline=True)
                    e.add_field(name="R2", value=r2, inline=True)
                    
                    # Create cropped image for thumbnail
                    img = Image.open(urlopen(row["image"]))
                    width, height = img.size
                    img_cropped = img.crop((300,220,width-300,height-220))
                    temp = BytesIO()
                    img_cropped.save(temp, img.format)
                    temp.seek(0)

                    file = discord.File(temp, filename="a.png")
                    e.set_thumbnail(url="attachment://a.png")

                    e.set_footer(text=f"Listing started at: {datetime.fromtimestamp(int(row['auction_info']['startingTimestamp']))}\nListing ending at: {datetime.fromtimestamp(int(row['auction_info']['endingTimestamp']))}")

                    await channel.send(file=file,embed=e)

                    self.send.append(row["id"])

    async def new_listings(self):
        """
        Uses GetAxieLatest to get the newly listed axies that fit our criteria
        """

        # Try, in case marketplace is down
        try:
            # Use the GraphQL query specified above, nly results section is important
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json={"query": axie_query, "operationName": axie_operationName, "variables": axie_variables,}) as r:
                        response = await r.json()
                        data = response["data"]["axies"]["results"]
            except Exception as e:
                print(e)
                print(
                    "Error with fetching new listings using GraphQL, trying again in 30 sec"
                )
                await asyncio.sleep(30)
                return

            # convert list to pandas DataFrame
            df = pd.DataFrame(data)

            # Specify columns
            df = df[["id", "auction", "class", "stage", "breedCount", "parts", "image", "stats"]]

            # Replace parts by their part name
            df["parts"] = [[d.get("name") for d in x] for x in df["parts"]]

            # Convert the parts to a set
            df["parts"] = df["parts"].apply(set)

            # Replace auction dict by current price in USD and convert it to numeric
            try:
                df["auction"] = pd.to_numeric(
                    df["auction"].apply(lambda x: x["currentPriceUSD"])
                )
            except Exception as e:
                print(e)

            # Check if any of these new listings are like the ones we are looking for
            for build in self.specifications:

                # Build a new dataframe for this search
                search = df.loc[
                    (df["class"].isin(build["Class"]))
                    & (df["breedCount"] <= build["Max Breedcount"])
                    & (df["auction"] < build["Max Price"])
                    & (set(build["Parts"]) <= df["parts"])
                ]

                # Only do this if it is not empty
                if not search.empty:
                    await self.send_alert(
                        await get_genes(search, build["R1 deviation"], build["R2 deviation"]),
                        build,
                    )

            # Send alert if there are axies with price less than 50$
            await self.send_alert(df.loc[df["auction"] < 50])

            # IMPLEMENT!
            # Add axies where startingPrice == endingPrice to seen
            # in old_listings() skip axies that have been seen

        except Exception as e:
            # Print out all the error information
            print(e)
            print(traceback.format_exc())
            print("Error at new_listings")

        # Check every 10 sec
        await asyncio.sleep(10)

    async def old_listings(self):
        """
        Uses getAxieBriefList to get the listed axies that fit our criteria
        """

        # Use the GraphQL query specified above, nly results section is important
        try:
            for build in self.specifications:
                from_var = 0
                not_done = True

                # Do this until the max price has been reached, increasing the limit with + 100 every time
                while not_done:
                    # Only works for 1 class
                    classes = json.dumps(build["Class"])
                    # Breed count is an array of numbers
                    if int(build["Max Breedcount"]) != 0:
                        # This only works if it is not 0
                        breedCount = list(range(int(build["Max Breedcount"])))
                    else:
                        breedCount = [0]

                    parts = json.dumps(build["Part Ids"])

                    # https://axie-graphql.web.app/operations/getAxieBriefList
                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.post(url, json={"query": old_axies_query, "operationName": old_axie_operationName, "variables": old_axie_variables(from_var, classes, breedCount, parts)}) as r:
                                response = await r.json()
                                data = response["data"]["axies"]["results"]
                    except Exception as e:
                        print(e)
                        print(
                            "Error with fetching old listings using GraphQL, trying again in 30 sec"
                        )
                        await asyncio.sleep(30)
                        return

                    df = pd.DataFrame(data)

                    # Specify columns
                    df = df[["id", "auction", "class", "breedCount", "parts", "image"]]

                    # Replace auction dict by current price in USD and convert it to numeric
                    try:
                        df["auction"] = pd.to_numeric(
                            df["auction"].apply(lambda x: x["currentPriceUSD"])
                        )
                    except Exception as e:
                        print(e)

                    # Only keep the ones with price less than max
                    search = df.loc[df["auction"] < build["Max Price"]]

                    # Only do this if it is not empty
                    if not search.empty:
                        await self.send_alert(
                            await get_genes(
                                search, build["R1 deviation"], build["R2 deviation"], True
                            ),
                            build,
                        )

                        # If there are enough axies fitting our search criteria
                        if len(search) == 100:
                            from_var += 100

                        # Stop the while loop otherwise
                        else:
                            not_done = False
                    else:
                        not_done = False

        except Exception as e:
            print(e)
            print(traceback.format_exc())
            await asyncio.sleep(120)
            return

        # Check every 5 minutes
        await asyncio.sleep(300)


def setup(bot):
    bot.add_cog(Alert(bot))
