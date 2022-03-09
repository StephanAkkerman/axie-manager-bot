##> Imports
import math
import sys

# > 3rd party dependencies
import pandas as pd
import gspread
import gspread_dataframe as gd
from urllib.request import urlopen
from PIL import Image
from io import BytesIO

# > Discord dependencies
import discord
from discord.ext import commands
from discord.ext.tasks import loop

# > Local dependencies
from alerts.api import api_genes, api_owner_axies
from config import config

# Login using the .json file
gc = gspread.service_account(filename="authentication.json")


class Axie_trades(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # This serves as a database, saves: "id", "auction", "class", "breedCount", "parts", "image", "price"
        self.axie_db = pd.DataFrame({})

        # Start function execution
        self.get_axie_auctions.start()

    # Could be quicker
    @loop(minutes=15)
    async def get_axie_auctions(self):
        """Main function that is looped every hour"""

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
            df = pd.concat([df, owned_axies], ignore_index=True)

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
            if len(new_ids) < len(old_ids):
                for id in diff:
                    await self.send_msg(self.axie_db, id, "sold")

            # Buy
            elif len(new_ids) > len(old_ids):
                for id in diff:
                    await self.send_msg(df, id, "bought")

            # No difference in ids
            else:
                # Check if price is not NaN
                new_auctions = df.loc[~df["price"].isna()]["id"].tolist()
                old_auctions = self.axie_db.loc[~self.axie_db["price"].isna()][
                    "id"
                ].tolist()

                # Difference: XOR
                auction_diff = list(set(new_auctions) ^ set(old_auctions))

                # New listing!
                if len(new_auctions) > len(old_auctions):
                    for id in auction_diff:
                        await self.send_msg(df, id, "is selling")

            # Update old db
            self.axie_db = df

    async def send_msg(self, df, id, keyword):
        """Sends a message in the discord channel"""

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
            r1_title = f"R1 ({genes['r1 deviation'].tolist()[0]})"
            r2_title = f"R2 ({genes['r2 deviation'].tolist()[0]})"

            for part in ["eyes", "ears", "mouth", "horn", "back", "tail"]:
                d += f"{(genes[part].tolist()[0]['d']['name'])}\n"
                r1 += f"{(genes[part].tolist()[0]['r1']['name'])}\n"
                r2 += f"{(genes[part].tolist()[0]['r2']['name'])}\n"

        else:
            d = r1 = r2 = "Unknown"
            r1_title = "R1"
            r2_title = "R2"

        # Send message in discord channel
        channel = discord.utils.get(
            self.bot.get_all_channels(),
            guild__name=config["DEBUG"]["GUILD_NAME"]
            if len(sys.argv) > 1 and sys.argv[1] == "-test"
            else config["DISCORD"]["GUILD_NAME"],
            name=config["LOOPS"]["AXIE_TRADES"]["CHANNEL"],
        )

        # Price
        if not math.isnan(row["price"].tolist()[0]):
            e = discord.Embed(
                title=f"{row['Manager'].tolist()[0]} {keyword} axie named {row['name'].tolist()[0]} for ${str(row['price'].tolist()[0])}",
                description="",
                url=link,
                color=0x00FFFF,
            )
        else:
            e = discord.Embed(
                title=f"{row['Manager'].tolist()[0]} {keyword} axie named {row['name'].tolist()[0]}",
                description="",
                url=link,
                color=0x00FFFF,
            )

        e.set_author(name="Axie Manager", icon_url=self.bot.user.avatar_url)

        # Breedcount
        e.add_field(
            name=":eggplant:",
            value=str(round(row["breedCount"].tolist()[0])),
            inline=True,
        )

        e.add_field(name="Class", value=row["class"].tolist()[0], inline=True)
        if "stats" in genes.columns:
            [
                e.add_field(name=stat[1:-5].capitalize(), value=stat[-2:], inline=True)
                for stat in str(genes["stats"].tolist()[0])[1:-28].split(", ")
            ]
        e.add_field(name="D", value=d, inline=True)
        e.add_field(name=r1_title, value=r1, inline=True)
        e.add_field(name=r2_title, value=r2, inline=True)

        # Create cropped image for thumbnail
        try:
            img = Image.open(urlopen(row["image"].tolist()[0]))
            width, height = img.size
            img_cropped = img.crop((300, 220, width - 300, height - 220))
            temp = BytesIO()
            img_cropped.save(temp, img.format)
            temp.seek(0)
            file = discord.File(temp, filename="a.png")
            e.set_thumbnail(url="attachment://a.png")
            await channel.send(file=file, embed=e)
        except Exception:
            pass

        await channel.send(embed=e)

    async def get_genes(self, id):
        """Takes axie id and returns its genes"""

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

        # Count deviations for every part
        for part in ["mouth", "horn", "back", "tail"]:
            genes[f"{part} r1"] = [0 if x["d"] == x["r1"] else 1 for x in genes[part]]
            genes[f"{part} r2"] = [0 if x["d"] == x["r2"] else 1 for x in genes[part]]

        # Sum all the deviations
        genes["r1 deviation"] = (
            genes["mouth r1"] + genes["horn r1"] + genes["back r1"] + genes["tail r1"]
        )
        genes["r2 deviation"] = (
            genes["mouth r2"] + genes["horn r2"] + genes["back r2"] + genes["tail r2"]
        )

        return genes

    async def get_addresses(self):
        """Gets all Ronin addresses in Scholars spreadsheet"""

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
        addresses = pd.concat([scholars, funds], ignore_index=True)

        # Replace ronin: with 0x for API
        addresses["Address"] = addresses["Address"].str.replace("ronin:", "0x")

        return addresses

    async def get_axies(self, address):
        """
        Processes api results and returns the dataframe
        """

        try:
            df = await api_owner_axies(address)
        except Exception:
            return pd.DataFrame({})

        # Replace parts by their part name, if there are any parts available
        if "parts" in df.columns:
            df["parts"] = [[d.get("name") for d in x] for x in df["parts"]]

        # Save the price in dataframe
        if "auction" in df.columns:
            df["price"] = pd.to_numeric(
                df["auction"].apply(lambda x: x["currentPriceUSD"] if x != None else x)
            )

        return df


def setup(bot):
    bot.add_cog(Axie_trades(bot))
