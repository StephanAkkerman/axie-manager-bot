#!/usr/bin/env python3

##> Imports
#> Standard library
import os
from datetime import datetime
import json

#> 3rd Party Dependencies
import discord
from discord.ext import commands
from cryptography.fernet import Fernet
import uuid

#> Local Dependencies
from scholars import getScholar
from QRCodeBot import *

# Get vars from .json
with open('authentication.json') as f:
    data = json.load(f)

fernet = Fernet(data['KEY'].encode("utf_8"))

# Bot prefix is !
bot = commands.Bot(command_prefix='!',  intents=discord.Intents.all())

@bot.event
async def on_ready():
    """ This gets printed on boot up"""

    guild = discord.utils.get(bot.guilds, name=data['TEST'])
    print(
        f"{bot.user} is connected to the following guild:\n"
        f"{guild.name}(id: {guild.id})"
    )

# Make this a toggle??
# @bot.event
# async def on_member_join(member):
#    """ Gives new users the role Tryout """
#    role = discord.utils.get(member.guild.roles, name="Tryout")
#    await member.add_roles(role)

# QR code bot
@bot.command()
async def qr(ctx):
    """ 
    Give users their qr code if they request it in the correct channel.
    Discord ID needs to be linked to Ronin Address and fernet encrypted privte key
    """

    # If the user writes !qr in the correct channel
    if ctx.channel.name == "🤖┃login":

        # Delete this message, to remove clutter
        await ctx.message.delete()

        # For logs
        current_time = datetime.now().strftime("%H:%M:%S")
        print("\n")

        # Get this scholars info from the sheet
        scholar_info = getScholar(ctx.message.author.id)

        # This for loop check for all the user's DiscordID in the Database
        if scholar_info != None:

            # Print log info
            print("This user received his QR Code : " + ctx.message.author.name)
            print("Discord ID : " + str(ctx.message.author.id))
            print("Current time : ", current_time)

            # discordID's encrypted privateKey from the sheets, as a string
            encrypted_key = scholar_info[1][2:-1]

            # Convert it to bytes and decrypt it, remove 0x
            accountPrivateKey = fernet.decrypt(
                encrypted_key.encode("utf_8")
            ).decode()[2:]

            # discordID's Ronin wallet from the database, replace ronin: with 0x
            accountAddress = scholar_info[0].replace("ronin:", "0x")

            # Get a message from AxieInfinty
            rawMessage = getRawMessage()

            # Sign that message with accountPrivateKey
            signedMessage = getSignMessage(rawMessage, accountPrivateKey)

            # Get an accessToken by submitting the signature to AxieInfinty
            accessToken = submitSignature(signedMessage, rawMessage, accountAddress)

            # Create a QrCode with that accessToken
            qrCodePath = f"QRCode_{ctx.message.author.id}_{str(uuid.uuid4())[0:8]}.png"
            qrcode.make(accessToken).save(qrCodePath)

            # Send the QrCode the the user who asked for it
            await ctx.message.author.send(
                "------------------------------------------------\n\n\nHello "
                + ctx.message.author.name
                + "\nHere is your new QR Code to login : "
            )
            await ctx.message.author.send(file=discord.File(qrCodePath))
            # Delete picture
            os.remove(qrCodePath)
            return

        # Scholar does not exist in sheet, maybe different Discord ID?
        else:
            print("This user didn't receive a QR Code : " + ctx.message.author.name)
            print("Discord ID : " + str(ctx.message.author.id))
            print("Current time : ", current_time)
            return

@bot.command()
async def encrypt(ctx, message=None):
    """
    Encrypts a user's message using your personal fernet key
    Message following !encrypt should not be empty
    """

    # If the user writes !encrypt followed by something else
    if ctx.channel.name == "🤖┃bots":

        # Error handling
        if message == None:
            await ctx.message.author.send("Please type something after !encrypt")
            return

        # Delete this message, for privacy
        await ctx.message.delete()

        # Encode private key
        encMessage = fernet.encrypt(message.encode())

        # Send a dm
        await ctx.message.author.send(
            "Hi "
            + ctx.message.author.name
            + ", here is your encrypted key:\n"
            + str(encMessage)
        )
        return

bot.run(data['TOKEN'])
