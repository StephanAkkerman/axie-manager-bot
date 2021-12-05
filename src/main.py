#!/usr/bin/env python3

##> Imports
# > Standard library
import os
import asyncio
import sys
import json

# > 3rd Party Dependencies
import discord
from discord.ext import commands

# Bot prefix is !
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
bot.remove_command("help")


@bot.event
async def on_ready():
    """This gets printed on boot up"""

    guild = discord.utils.get(
        bot.guilds,
        name=data["TEST"]
        if len(sys.argv) > 1 and sys.argv[1] == "-test"
        else data["GUILD"],
    )

    print(
        f"{bot.user} is connected to the following guild:\n"
        f"{guild.name}(id: {guild.id})"
    )

    # Load all loops
    for filename in os.listdir("./src/cogs/loops"):
        if filename.endswith(".py"):
            print("Loading:", filename)
            bot.load_extension(f"cogs.loops.{filename[:-3]}")


if __name__ == "__main__":
    # Load all commands
    for filename in os.listdir("./src/cogs/commands"):
        if filename.endswith(".py"):
            print("Loading:", filename)
            bot.load_extension(f"cogs.commands.{filename[:-3]}")

    # Load all listeners
    for filename in os.listdir("./src/cogs/listeners"):
        if filename.endswith(".py"):
            print("Loading:", filename)
            bot.load_extension(f"cogs.listeners.{filename[:-3]}")

    # Get vars from .json
    with open("authentication.json") as f:
        data = json.load(f)

    TOKEN = (
        data["TEST_TOKEN"]
        if len(sys.argv) > 1 and sys.argv[1] == "-test"
        else data["TOKEN"]
    )

    # Main event loop
    try:
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
