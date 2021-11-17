##> Imports
# > 3rd party dependencies
import pandas as pd
import gspread
import gspread_dataframe as gd
import aiohttp
from tenacity import retry, stop_after_attempt, wait_fixed
from urllib.request import urlopen
from PIL import Image
from io import BytesIO

# > Discord dependencies
import discord
from discord.ext import commands
from discord.ext.tasks import loop

# > Local dependencies
from alerts.api import api_genes

# Login using the .json file
gc = gspread.service_account(filename="authentication.json")


class Activity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # This serves as a database, saves: "id", "auction", "class", "breedCount", "parts", "image", "price"
        self.axie_db = pd.DataFrame({})

        # Start function execution
        self.get_axie_auctions.start()

    @loop(hours=1)
    async def get_axie_auctions(self):
        """ Main function that is looped every hour """

        # Save all important data in dataframe
        df = pd.DataFrame({})

        # Get the address dataframe
        address_df = await self.get_addresses()
        addresses = address_df["Address"].tolist()

        # Do this for every address in the dataframe
        for address in addresses:
            owned_axies = await self.get_axies(address)
            owned_axies["Manager"] = address_df.loc[address_df["Address"] == address][
                "Manager"
            ].tolist()[0]
            df = df.append(owned_axies)

        # If axie_ids is empty
        if self.axie_db.empty:
            self.axie_db = df
        # Compare
        else:
            # Get all ids of current axies
            new_ids = df["id"].tolist()
            old_ids = self.axie_db["id"].tolist()

            # Difference: XOR
            diff = list(set(new_ids) ^ set(old_ids))

            # Sold
            if new_ids < old_ids:
                for id in diff:
                    await self.send_msg(df, self.axie_db, "sold")

            # Buy
            elif new_ids > old_ids:
                for id in diff:
                    await self.send_msg(df, id, "bought")

            # No difference in ids
            else:
                new_auctions = df.loc[df["auction"] != None]["id"].tolist()
                old_auctions = self.axie_db.loc[self.axie_db["auction"] != None][
                    "id"
                ].tolist()

                # Difference: XOR
                auction_diff = list(set(new_auctions) ^ set(old_auctions))

                # New listing!
                if new_auctions > old_auctions:
                    for id in auction_diff:
                        await self.send_msg(df, id, "is selling")

    async def send_msg(self, df, id, keyword):
        """ Sends a message in the discord channel """

        # Set variables based on id and df
        row = df.loc[df["id"] == id]
        link = (
            "https://marketplace.axieinfinity.com/axie/" + row["id"].tolist()[0] + "/"
        )

        # Call genes api
        genes = await self.get_genes(id)

        if not genes.empty:
            d = ""
            r1 = ""
            r2 = ""

            for part in ["eyes", "ears", "mouth", "horn", "back", "tail"]:
                d += f"{(genes[part].tolist()[0]['d']['name'])}\n"
                r1 += f"{(genes[part].tolist()[0]['r1']['name'])}\n"
                r2 += f"{(genes[part].tolist()[0]['r2']['name'])}\n"

        else:
            d = r1 = r2 = "Unknown"

        # Send message in discord channel
        channel = discord.utils.get(
            self.bot.get_all_channels(),
            guild__name="Axie Manager Scholar Group"
            if self.bot.user.id == 892855262124326932
            else "Bot Test Server",
            name="🤝┃axie-trades",
        )

        e = discord.Embed(
            title=f"{row['Manager'].tolist()[0]} {keyword}",
            description="",
            url=link,
            color=0x00FFFF,
        )

        e.set_author(name="Axie Manager", icon_url=self.bot.user.avatar_url)

        # Price
        if "price" in row.columns:
            e.add_field(
                name="Price", value=f"${str(row['price'].tolist()[0])}\n", inline=True,
            )

        # Breedcount
        e.add_field(
            name=":eggplant:", value=str(row["breedCount"].tolist()[0]), inline=True
        )

        e.add_field(name="Class", value=row["class"].tolist()[0], inline=True)
        [
            e.add_field(name=stat[1:-5].capitalize(), value=stat[-2:], inline=True)
            for stat in str(genes["stats"].tolist()[0])[1:-28].split(", ")
        ]
        e.add_field(name="D", value=d, inline=True)
        e.add_field(name="R1", value=r1, inline=True)
        e.add_field(name="R2", value=r2, inline=True)

        # Create cropped image for thumbnail
        img = Image.open(urlopen(row["image"].tolist()[0]))
        width, height = img.size
        img_cropped = img.crop((300, 220, width - 300, height - 220))
        temp = BytesIO()
        img_cropped.save(temp, img.format)
        temp.seek(0)

        file = discord.File(temp, filename="a.png")
        e.set_thumbnail(url="attachment://a.png")

        await channel.send(file=file, embed=e)

    async def get_genes(self, id):
        """ Takes axie id and returns its genes """

        try:
            response = await api_genes(id)
        except Exception as e:
            print(e)
            print("Error fetching api_genes")
            # Return an empty dataframe, so no crashes will occur
            return pd.DataFrame({})

        df = pd.DataFrame.from_dict(response, orient="index")
        genes = df.transpose()

        if genes["stage"].tolist()[0] == 1:
            return pd.DataFrame({})

        for part in ["eyes", "ears", "mouth", "horn", "back", "tail"]:
            genes[part] = genes["traits"].apply(lambda x: x[part])

        return genes

    async def get_addresses(self):
        """ Gets all Ronin addresses in Scholars spreadsheet """

        # Open Scholars spreadsheet
        sheet = gc.open("Scholars")

        # Get the Scholars and Funds worksheet as dataframe
        scholars = (
            gd.get_as_dataframe(sheet.worksheet("Scholars"))
            .dropna(axis=0, how="all")
            .dropna(axis=1, how="all")
        )
        funds = (
            gd.get_as_dataframe(sheet.worksheet("Funds"))
            .dropna(axis=0, how="all")
            .dropna(axis=1, how="all")
        )

        # We only care about these columns
        scholars = scholars[["Manager", "Address"]]
        funds = funds.rename(columns={"Funds Address": "Address"})

        # Merge the dataframes
        addresses = scholars.append(funds).reset_index(drop=True)

        # Replace ronin: with 0x for API
        addresses["Address"] = addresses["Address"].str.replace("ronin:", "0x")

        return addresses

    @retry(stop=stop_after_attempt(12), wait=wait_fixed(5))
    async def api_axies(self, address):
        """ 
        Gets axies of specific Ronin address
        Returns a dataframe consisting of columns "id", "auction", "class", "breedCount", "parts", "image", "price"
        """

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://axieinfinity.com/graphql-server-v2/graphql",
                json={
                    "query": "query GetAxieBriefList($auctionType: AuctionType, $criteria: AxieSearchCriteria, $from: Int, $sort: SortBy, $size: Int, $owner: String) {\n  axies(auctionType: $auctionType, criteria: $criteria, from: $from, sort: $sort, size: $size, owner: $owner) {\n    total\n    results {\n      ...AxieBrief\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment AxieBrief on Axie {\n  id\n  name\n  stage\n  class\n  breedCount\n  image\n  title\n  battleInfo {\n    banned\n    __typename\n  }\n  auction {\n    currentPrice\n    currentPriceUSD\n    __typename\n  }\n  parts {\n    id\n    name\n    class\n    type\n    specialGenes\n    __typename\n  }\n  __typename\n}\n",
                    "operationName": "GetAxieBriefList",
                    "variables": {"owner": address},
                },
            ) as r:
                response = await r.json()
                return pd.DataFrame(response["data"]["axies"]["results"])[
                    ["id", "auction", "class", "breedCount", "parts", "image"]
                ]

    async def get_axies(self, address):
        """
        Processes api results and returns the dataframe
        """

        df = await self.api_axies(address)

        # Replace parts by their part name
        df["parts"] = [[d.get("name") for d in x] for x in df["parts"]]

        # Save the price in dataframe
        try:
            df["price"] = pd.to_numeric(
                df["auction"].apply(lambda x: x["currentPriceUSD"])
            )
        # Can only be done if there is an auction going on
        except TypeError:
            pass

        return df


def setup(bot):
    bot.add_cog(Activity(bot))
