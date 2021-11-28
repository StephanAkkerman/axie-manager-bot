##> Imports
# > Standard libraries
import json
import traceback
from datetime import datetime
import asyncio

# > Discord dependencies
import discord
from discord.ext import commands
from discord.ext.tasks import loop

# > 3rd party dependencies
import pandas as pd  # For parsing data
from urllib.request import urlopen
from PIL import Image
from io import BytesIO

# > Local dependencies
from alerts.graphql import *
from alerts.builds import get_builds
from alerts.genes import get_genes
from alerts.api import api_new_listings, api_old_listings, api_axie_details


class Alert(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.send = []
        self.new = []
        self.specifications = []
        self.new_builds.start()

        # Start functions
        self.new_listings.start()
        self.old_listings.start()

        # Helper functions
        self.clear_send.start()
        self.clear_new.start()

    @loop(hours=5)
    async def clear_send(self):
        """Clears the send list every 5 hours"""
        self.send = []

    @loop(hours=1)
    async def new_builds(self):
        """Gets the new builds every hour"""
        self.specifications = get_builds()

    @loop(seconds=120)
    async def clear_new(self):
        """Clears the new list every 2 minutes"""
        self.new = []

    async def send_alert(self, axie_df, build):
        """
        Takes an axie dataframe and build and sends a message in the discord channel for each of them
        """

        if not axie_df.empty:
            for _, row in axie_df.iterrows():
                if row["id"] not in self.send:
                    link = (
                        "https://marketplace.axieinfinity.com/axie/" + row["id"] + "/"
                    )

                    # For setting the right D, R1, and R2
                    d = ""
                    r1 = ""
                    r2 = ""
                    r1_title = f"R1 ({row['r1 deviation']})"
                    r2_title = f"R2 ({row['r2 deviation']})"

                    for part in ["eyes", "ears", "mouth", "horn", "back", "tail"]:
                        d += f"{(row[part]['d']['name'])}\n"
                        r1 += f"{(row[part]['r1']['name'])}\n"
                        r2 += f"{(row[part]['r2']['name'])}\n"

                    # Send message in discord channel
                    channel = discord.utils.get(
                        self.bot.get_all_channels(),
                        guild__name="Axie Manager Scholar Group"
                        if self.bot.user.id == 892855262124326932
                        else "Bot Test Server",
                        name="💎┃bot-alerts",
                    )

                    e = discord.Embed(
                        title=f"{build['Name']} {row['r1 deviation']} - {row['r2 deviation']}",
                        description="",
                        url=link,
                        color=0x00FFFF,
                    )

                    # Maybe improve this
                    if row["auction"] == None:

                        updated_info = await api_axie_details(row["id"])

                        if updated_info["auction"].tolist()[0] == None:
                            start_price = row["price"]
                            end_price = row["price"]
                            start_time = datetime.now().strftime("%Y-%m-%d")
                            end_time = datetime.now().strftime("%Y-%m-%d")
                        else:
                            start_price = int(
                                updated_info["auction"].tolist()[0]["startingPrice"]
                            )
                            end_price = int(
                                updated_info["auction"].tolist()[0]["endingPrice"]
                            )
                            start_time = datetime.fromtimestamp(
                                int(
                                    updated_info["auction"].tolist()[0][
                                        "startingTimestamp"
                                    ]
                                )
                            )
                            end_time = datetime.fromtimestamp(
                                int(
                                    updated_info["auction"].tolist()[0][
                                        "endingTimestamp"
                                    ]
                                )
                            )
                    else:
                        start_price = int(row["auction"]["startingPrice"])
                        end_price = int(row["auction"]["endingPrice"])
                        start_time = datetime.fromtimestamp(
                            int(row["auction"]["startingTimestamp"])
                        )
                        end_time = datetime.fromtimestamp(
                            int(row["auction"]["endingTimestamp"])
                        )

                    e.set_author(name="Axie Manager", icon_url=self.bot.user.avatar_url)

                    e.add_field(
                        name="Current Price",
                        value=f"${str(row['price'])}\n",
                        inline=True,
                    )
                    e.add_field(
                        name="Starting price",
                        value=f"Ξ{round(start_price * 0.000000000000000001, 3)}\n",
                        inline=True,
                    )
                    e.add_field(
                        name="Ending price",
                        value=f"Ξ{round(end_price * 0.000000000000000001, 3)}\n",
                        inline=True,
                    )

                    e.add_field(
                        name=":eggplant:", value=str(row["breedCount"]), inline=True
                    )
                    e.add_field(name="Class", value=row["class"], inline=True)
                    [
                        e.add_field(
                            name=stat[1:-5].capitalize(), value=stat[-2:], inline=True
                        )
                        for stat in str(row["stats"])[1:-28].split(", ")
                    ]

                    e.add_field(name="D", value=d, inline=True)
                    e.add_field(name=r1_title, value=r1, inline=True)
                    e.add_field(name=r2_title, value=r2, inline=True)

                    # Create cropped image for thumbnail
                    try:
                        img = Image.open(urlopen(row["image"]))
                        width, height = img.size
                        img_cropped = img.crop((300, 220, width - 300, height - 220))
                        temp = BytesIO()
                        img_cropped.save(temp, img.format)
                        temp.seek(0)

                        file = discord.File(temp, filename="a.png")
                        e.set_thumbnail(url="attachment://a.png")
                    except Exception:
                        pass

                    e.set_footer(
                        text=f"Listing started at: {start_time}\nListing ending at: {end_time}"
                    )

                    msg = await channel.send(file=file, embed=e)
                    await msg.add_reaction("\N{GEM STONE}")

                    self.send.append(row["id"])

                    if (
                        "Discord Name" in build
                        and build["Discord Name"] == build["Discord Name"]
                    ):
                        users = [
                            user
                            for user in self.bot.get_all_members()
                            if user.name in build["Discord Name"]
                        ]
                        mentions = ""
                        for user in users:
                            mentions += f"<@{user.id}> "
                        await channel.send(mentions)

    @loop(seconds=10)
    async def new_listings(self):
        """
        Uses GetAxieLatest to get the newly listed axies that fit our criteria
        """

        # Try, in case marketplace is down
        try:
            # Use the GraphQL query specified above, only results section is important
            try:
                # Get a dataframe of the new listings
                df = await api_new_listings()
            except Exception as e:
                print(e)
                print(
                    "Error with fetching new listings using GraphQL, trying again in 5 minutes"
                )
                # Wait 5 minutes
                await asyncio.sleep(300)
                return

            # Replace parts by their part name
            df["parts"] = [[d.get("name") for d in x] for x in df["parts"]]

            # Convert the parts to a set
            df["parts"] = df["parts"].apply(set)

            # Replace auction dict by current price in USD and convert it to numeric
            try:
                df["price"] = pd.to_numeric(
                    df["auction"].apply(lambda x: x["currentPriceUSD"])
                )
                df['hp'] = pd.to_numeric(
                    df["stats"].apply(lambda x: x["hp"])
                )
                df['morale'] = pd.to_numeric(
                    df["stats"].apply(lambda x: x["morale"])
                )
                df['speed'] = pd.to_numeric(
                    df["stats"].apply(lambda x: x["speed"])
                )
                df['skill'] = pd.to_numeric(
                    df["stats"].apply(lambda x: x["skill"])
                )
            except Exception as e:
                print(e)

            # Check if any of these new listings are like the ones we are looking for
            for build in self.specifications:
                
                # Build a new dataframe for this search
                search = df.loc[
                    (df["class"].isin(build["Class"]))
                    & (df["breedCount"] <= build["Max Breedcount"])
                    & (df["price"] < build["Max Price"])
                    & (set(build["Parts"]) <= df["parts"])
                    & (df["hp"] >= build["Hp"])
                    & (df["morale"] >= build['Morale'])
                    & (df["speed"] >= build['Speed'])
                    & (df["skill"] >= build['Skill'])
                ]

                # Remove ids we have already seen the last minute
                search = search.loc[~search.id.isin(self.new)]

                # Only do this if it is not empty
                if not search.empty:
                    self.new.append(search.id)
                    await self.send_alert(
                        await get_genes(
                            search, build["R1 deviation"], build["R2 deviation"]
                        ),
                        build,
                    )

            # IMPLEMENT!
            # Add axies where startingPrice == endingPrice to seen
            # in old_listings() skip axies that have been seen

        except Exception as e:
            # Print out all the error information
            print(e)
            print(traceback.format_exc())
            print("Error at new_listings")

    @loop(seconds=300)
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
                    # Breed count is an array of numbers
                    if int(build["Max Breedcount"]) != 0:
                        # This only works if it is not 0
                        breedCount = list(range(int(build["Max Breedcount"])))
                    else:
                        breedCount = [0]
                        
                    classes = json.dumps(build["Class"])
                    parts = json.dumps(build["Part Ids"])
                    # Stats max is always 61
                    hp = [build['Hp'], 61]
                    speed = [build['Speed'], 61]
                    skill = [build['Skill'], 61]
                    morale = [build['Morale'], 61]

                    # https://axie-graphql.web.app/operations/getAxieBriefList
                    try:
                        df = await api_old_listings(
                            from_var, classes, breedCount, parts, hp, speed, skill, morale
                        )
                    except Exception as e:
                        print(e)
                        print(
                            "Error with fetching old listings using GraphQL, trying again in 5 minutes"
                        )
                        # Return because otherwise the rest does not work
                        await asyncio.sleep(300)
                        return

                    # Replace auction dict by current price in USD and convert it to numeric
                    try:
                        df["price"] = pd.to_numeric(
                            df["auction"].apply(lambda x: x["currentPriceUSD"])
                        )
                    except Exception as e:
                        print(e)
                        
                    # Only keep the ones with price less than max
                    search = df.loc[df["price"] < build["Max Price"]]

                    # Only do this if it is not empty
                    if not search.empty:
                        await self.send_alert(
                            await get_genes(
                                search,
                                build["R1 deviation"],
                                build["R2 deviation"],
                                True,
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


def setup(bot):
    bot.add_cog(Alert(bot))
