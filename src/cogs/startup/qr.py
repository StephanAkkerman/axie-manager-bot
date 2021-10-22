# Standard library
from discord.ext.commands.core import has_role
import requests
import json
import os
import uuid
from datetime import datetime

# Third Party Dependencies
import qrcode
from web3.auto import w3
from eth_account.messages import encode_defunct

# Discord imports
import discord
from discord.ext import commands

# Local files
from scholars import getScholar
from cogs.startup.encrypt import fernet


class QR(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["code", "login"])
    @commands.has_role("Verified")
    async def qr(self, ctx):
        """Give users their qr code if they request it in the correct channel.

        Discord ID needs to be linked to Ronin Address and fernet encrypted private key
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
                qrCodePath = (
                    f"QRCode_{ctx.message.author.id}_{str(uuid.uuid4())[0:8]}.png"
                )
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

                await ctx.message.author.send(
                    "Sorry, something went wrong when trying to load your personal QR code. Please contact a manager."
                )
                return

    @qr.error
    async def qr_error(self, ctx, error):
        # Delete this message, to remove clutter
        await ctx.message.delete()

        if isinstance(error, commands.MissingRole):
            channel = discord.utils.get(ctx.guild.channels, name="👋┃welcome")
            channel_id = channel.id
            await ctx.message.author.send(
                f"Sorry, you cannot use this command yet, since you are not verified. You can get verified in the <#{channel_id}> channel."
            )


def getRawMessage():
    # Function to get message to sign from axie

    # An exemple of a requestBody needed
    requestBody = {
        "operationName": "CreateRandomMessage",
        "variables": {},
        "query": "mutation CreateRandomMessage {\n  createRandomMessage\n}\n",
    }
    # Send the request
    r = requests.post(
        "https://axieinfinity.com/graphql-server-v2/graphql",
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
        },
        data=requestBody,
    )
    # Load the data into json format
    json_data = json.loads(r.text)
    # Return the message to sign
    return json_data["data"]["createRandomMessage"]


def getSignMessage(rawMessage, accountPrivateKey):
    # Function to sign the message got from getRawMessage function

    # Load the private key from the DataBase in Hex
    private_key = bytearray.fromhex(accountPrivateKey)
    message = encode_defunct(text=rawMessage)
    # Sign the message with the private key
    hexSignature = w3.eth.account.sign_message(message, private_key=private_key)
    # Return the signature
    return hexSignature


def submitSignature(signedMessage, message, accountAddress):
    # Function to submit the signature and get authorization

    # An example of a requestBody needed
    requestBody = {
        "operationName": "CreateAccessTokenWithSignature",
        "variables": {
            "input": {
                "mainnet": "ronin",
                "owner": "User's Eth Wallet Address",
                "message": "User's Raw Message",
                "signature": "User's Signed Message",
            }
        },
        "query": "mutation CreateAccessTokenWithSignature($input: SignatureInput!) {\n  createAccessTokenWithSignature(input: $input) {\n    newAccount\n    result\n    accessToken\n    __typename\n  }\n}\n",
    }
    # Remplace in that example to the actual signed message
    requestBody["variables"]["input"]["signature"] = signedMessage["signature"].hex()
    # Remplace in that example to the actual raw message
    requestBody["variables"]["input"]["message"] = message
    # Remplace in that example to the actual account address
    requestBody["variables"]["input"]["owner"] = accountAddress
    # Send the request
    r = requests.post(
        "https://axieinfinity.com/graphql-server-v2/graphql",
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
        },
        json=requestBody,
    )
    # Load the data into json format
    json_data = json.loads(r.text)
    # Return the accessToken value
    return json_data["data"]["createAccessTokenWithSignature"]["accessToken"]


def setup(bot):
    bot.add_cog(QR(bot))
