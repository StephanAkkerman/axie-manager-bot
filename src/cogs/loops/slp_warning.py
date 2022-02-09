##> Imports
# > Standard libraries
import asyncio
from datetime import datetime, timedelta, time
import sys

# > 3rd party dependencies
from dateutil.relativedelta import relativedelta
from discord import player
import gspread
import gspread_dataframe as gd
import pandas as pd

# > Discord dependencies
import discord
from discord.ext import commands
from discord.ext.tasks import loop

# > Local dependencies
from cogs.commands.encrypt import fernet
from cogs.commands.qr import getRawMessage, getSignMessage, submitSignature
from alerts.api import api_missions, api_player, api_game_api
from config import config

gc = gspread.service_account(filename="authentication.json")

# One hour before daily reset
WHEN = time(hour=23, minute=0, second=0)


class Slp_warning(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Start loops
        self.background_task.start()

    async def slp_warning(self):

        # Open Scholars worksheet
        ws = gc.open("Scholars").worksheet("Scholars")

        # Convert to DataFrames
        df = gd.get_as_dataframe(ws).dropna(axis=0, how="all").dropna(axis=1, how="all")

        # discordID's encrypted privateKey from the sheets, as a string
        df["Info"] = df["Info"].str[2:-1]

        # Convert it to bytes and decrypt it, remove 0x
        df["Info"] = df["Info"].apply(
            lambda x: fernet.decrypt(x.encode("utf_8")).decode()[2:]
        )

        # Get MMR of all scholars
        mmr = await api_game_api(",".join(df["Address"].tolist()))
        df["MMR"] = mmr["mmr"].tolist()

        # Save data in results dict
        results = {}

        # Iterate over all the dataframes
        for _, row in df.iterrows():
            scholar = row["Scholar Name"]
            address = row["Address"]
            private_key = row["Info"]

            # Get a message from AxieInfinty
            rawMessage = getRawMessage()

            # Sign that message with accountPrivateKey
            signedMessage = getSignMessage(rawMessage, private_key)

            # Get an accessToken by submitting the signature to AxieInfinty
            accessToken = submitSignature(
                signedMessage, rawMessage, address.replace("ronin:", "0x")
            )

            # Skip accounts that return nothing
            try:
                missions = await api_missions(address, accessToken)
                player_info = await api_player(address, accessToken)
            except Exception:
                print(f"Could not get slp warning data for scholar: {scholar}")
                continue

            # Keep track of missions that are not yet done
            add_to_list = False
            not_done = []
            for mission_dict in missions:
                if mission_dict["progress"] < mission_dict["total"]:
                    add_to_list = True
                    #if mission_dict["name"] == "Check in":
                    #    not_done.append(
                    #        ":x: You have not yet claimed the daily check in reward."
                    #    )
                    #elif mission_dict["name"] == "PvE":
                    #    not_done.append(
                    #        f":x: You currenlty only played {mission_dict['progress']}/{mission_dict['total']} PvE games."
                    #    )
                    if mission_dict["name"] == "PvP":
                        not_done.append(
                            f":x: You currenlty only played {mission_dict['progress']}/{mission_dict['total']} PvP games."
                        )

            if player_info["remaining_energy"] == 20:
                not_done.append(
                    f":x: You have {player_info['remaining_energy']} energy remaining."
                )
                add_to_list = True

            #if player_info["pve_slp_gained_last_day"] < 50:
            #    not_done.append(
            #        f":x: You only have {player_info['pve_slp_gained_last_day']}/50 adventure SLP completed."
            #    )
            #    add_to_list = True

            if row["MMR"] < 800:
                not_done.append(
                    f":x: You are only at {row['MMR']} MMR in arena. <800 = no SLP."
                )
                add_to_list = True

            # Add it to the results dictionary
            if add_to_list:
                results[scholar] = not_done

        channel = discord.utils.get(
            self.bot.get_all_channels(),
            guild__name=config["DEBUG"]["GUILD_NAME"]
            if len(sys.argv) > 1 and sys.argv[1] == "-test"
            else config["DISCORD"]["GUILD_NAME"],
            name=config["LOOPS"]["SLP_WARNING"]["CHANNEL"],
        )

        message = "The daily rest is in 1 hour!\n"

        # Add to message for each scholar
        for scholar, not_done in results.items():
            user = [user for user in self.bot.get_all_members() if user.name == scholar]
            try:
                message += f"<@{user[0].id}>:\n"
            except Exception:
                message += f"{scholar}:\n"

            for nd in not_done:
                message += f"{nd}\n"
            message += "\n"

        # Send message
        await channel.send(message)

    # From https://stackoverflow.com/questions/63769685/discord-py-how-to-send-a-message-everyday-at-a-specific-time
    @loop(hours=24)
    async def background_task(self):
        now = datetime.utcnow()
        if (
            now.time() > WHEN
        ):  # Make sure loop doesn't start after {WHEN} as then it will send immediately the first time as negative seconds will make the sleep yield instantly
            tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))
            seconds = (
                tomorrow - now
            ).total_seconds()  # Seconds until tomorrow (midnight)
            await asyncio.sleep(
                seconds
            )  # Sleep until tomorrow and then the loop will start

        while True:
            now = (
                datetime.utcnow()
            )  # You can do now() or a specific timezone if that matters, but I'll leave it with utcnow
            target_time = datetime.combine(now.date(), WHEN)  # 6:00 PM today (In UTC)
            seconds_until_target = (target_time - now).total_seconds()
            await asyncio.sleep(
                seconds_until_target
            )  # Sleep until we hit the target time
            await self.slp_warning()  # Call the helper function that sends the message
            tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))
            seconds = (
                tomorrow - now
            ).total_seconds()  # Seconds until tomorrow (midnight)
            await asyncio.sleep(
                seconds
            )  # Sleep until tomorrow and then the loop will start a new iteration


def setup(bot):
    bot.add_cog(Slp_warning(bot))
