# Standard libraries
import asyncio
import os
import sys

# Third party libraries
from cryptography.fernet import Fernet
import gspread
import yaml

# Discord imports
import discord
from discord.ext import commands
from discord.utils import get

# Login using the .json file
gc = gspread.service_account(filename="authentication.json")

# Read config.yaml content
with open("config_example.yaml", "r", encoding="utf-8") as f:
    config = yaml.full_load(f)

# Set the bot
bot = commands.Bot(command_prefix=config["PREFIX"], intents=discord.Intents.all())


def create_scholars_sheet():
    """Create a new Scholars spreadsheet"""
    try:
        sheet = gc.open("Scholars")
        print("Found existing Scholars spreadsheet")
    except gspread.exceptions.SpreadsheetNotFound:
        sheet = gc.create("Scholars", folder_id)
        print("Creating Scholars spreadsheet")

    # Create the worksheets
    try:
        ws = sheet.worksheet("Scholars")
        print("Found existing Scholars worksheet")
    # If it does not exist, make one
    except gspread.exceptions.WorksheetNotFound:
        ws = gc.open("Scholars").add_worksheet(title="Scholars", rows="100", cols="20")
        print("Creating Scholars worksheet")

    # Add the default first row
    ws.update(
        "A1:F1",
        [
            [
                "Scholar Name",
                "Manager",
                "Scholar Share",
                "Address",
                "Payout Address",
                "Info",
            ]
        ],
    )

    # Create the worksheet
    try:
        ws = sheet.worksheet("Funds")
        print("Found existing Funds worskheet")
    except gspread.exceptions.WorksheetNotFound:
        ws = gc.open("Scholars").add_worksheet(title="Funds", rows="100", cols="20")
        print("Creating Funds worksheet")

    # Add the default first row
    ws.update("A1:B1", [["Manager", "Funds Address"]])


def create_axie_builds_sheet():
    try:
        sheet = gc.open("Axie Builds")
        print("Found existing Axie Builds spreadsheet")
    except gspread.exceptions.SpreadsheetNotFound:
        sheet = gc.create("Axie Builds", folder_id)
        print("Creating Axie Builds spreadsheet")

    # Create the worksheet
    try:
        ws = sheet.worksheet("main")
        print("Found existing main worskheet")

    # If it does not exist, make one
    except gspread.exceptions.WorksheetNotFound:
        ws = gc.open("Axie Builds").add_worksheet(title="main", rows="100", cols="20")
        print("Creating main worksheet")

    ws.update(
        "A1:L1",
        [
            [
                "Name",
                "Class",
                "Max Price",
                "Max Breedcount",
                "Parts (Axie ID)",
                "Hp",
                "Morale",
                "Speed",
                "Skill",
                "R1 deviation",
                "R2 deviation",
                "Discord Name",
            ]
        ],
    )


@bot.event
async def on_ready():
    guild = get(
        bot.guilds,
        name=config["DEBUG"]["GUILD_NAME"]
        if len(sys.argv) > 1 and sys.argv[1] == "-test"
        else config["DISCORD"]["GUILD_NAME"],
    )

    # Check if roles exists, if not make them
    for role in [
        config["ROLES"]["VERIFIED"],
        config["ROLES"]["TRYOUT"],
        config["ROLES"]["SCHOLAR"],
        config["ROLES"]["MANAGER"],
        config["ROLES"]["MUTE"],
    ]:
        if get(guild.roles, name=role) is None:
            await guild.create_role(name=role)
            print(f"Created role: {role}")

    # Maybe automate this process
    channels = [
        config["WELCOME_CHANNEL"],
        config["ERROR"]["CHANNEL"],
        config["LOOPS"]["AXIE_ALERT"]["CHANNEL"],
        config["LOOPS"]["AXIE_TRADES"]["CHANNEL"],
        config["LOOPS"]["CLEAN_CHANNEL"]["CHANNEL"],
        config["LOOPS"]["INSTAGRAM"]["CHANNEL"],
        config["LOOPS"]["LEADERBOARD"]["CHANNEL"],
        config["LOOPS"]["PRICES"]["CHANNEL"],
        config["LOOPS"]["SLP_WARNING"]["CHANNEL"],
        config["COMMANDS"]["QR"]["CHANNEL"],
        config["LISTENERS"]["ON_MESSAGE"]["CHANNEL"],
        config["LISTENERS"]["TRANSLATE"]["CHANNEL"],
    ]

    # Check if channel exists, if not make them
    for channel in channels:
        if get(guild.text_channels, name=channel) is None:
            await guild.create_text_channel(channel)
            print(f"Created channel: {channel}")

    # Rename config_example to config.yaml, check if there is no config.yaml yet
    os.rename("config_example.yaml", "config.yaml")

    # Print this to the console
    print("In config.yaml add this behind KEY: (line 103)")
    print(str(Fernet.generate_key())[2:-2])
    print()
    print("After doing that, close this screen and start the bot with the command:")
    print("python src/main.py")


if __name__ == "__main__":

    # Request the folder id
    folder_id = input(
        "Please paste the folder url that you shared with the bot, e.g. https://drive.google.com/drive/folders/abcdlakfdj:\n"
    )

    # Get everything after the last /
    folder_id = folder_id.split("/")[-1]

    # Create the Scholars spreadsheet + worksheet
    create_scholars_sheet()

    # Create the axie-builds spreadsheet, if turned on
    if config["LOOPS"]["AXIE_ALERT"]["ENABLED"]:
        create_axie_builds_sheet()

    TOKEN = (
        config["DEBUG"]["TOKEN"]
        if len(sys.argv) > 1 and sys.argv[1] == "-test"
        else config["DISCORD"]["TOKEN"]
    )

    # Main event loop
    try:
        print("Trying..")
        bot.loop.run_until_complete(bot.run(TOKEN))
    except KeyboardInterrupt:
        print("Caught interrupt signal.")
        print("exiting...")
        bot.loop.run_until_complete(
            asyncio.wait(
                [bot.change_presence(status=discord.Status.invisible), bot.logout()]
            )
        )
    finally:
        bot.loop.close()
        sys.exit(0)
