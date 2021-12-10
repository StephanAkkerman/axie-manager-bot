##> Imports
# > Standard library
from discord.ext.commands.core import has_role
import requests
import json
import os
import uuid
from datetime import datetime
import traceback

# > 3rd party dependencies
import qrcode
from web3.auto import w3
from eth_account.messages import encode_defunct
import gspread
import gspread_dataframe as gd

# > Discord imports
import discord
from discord.ext import commands

# > Local files
from cogs.commands.encrypt import fernet
from config import config

gc = gspread.service_account(filename="authentication.json")


class QR(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["code", "login", " qr"])
    @commands.has_role(config['ROLES']['SCHOLAR'])
    async def qr(self, ctx):
        """Request your personal QR code

        Usage: `!qr`
        Request your personal QR code to log in. This has to be done in the dedicated login channel.
        _Note_: Your Discord ID needs to be linked to Ronin Address and fernet encrypted private key. Please contact your manager to do so.
        """

        # If the user writes !qr in the correct channel
        if ctx.channel.name == config['COMMANDS']['QR']['CHANNEL']:

            # Delete this message, to remove clutter
            await ctx.message.delete()

            # For logs
            current_time = datetime.now().strftime("%H:%M:%S")
            print("\n")

            # Get this scholars info from the sheet
            scholar_info = getScholar(ctx.message.author.name)

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

            # Scholar does not exist in sheet, maybe different Discord ID?
            else:
                raise commands.MemberNotFound(ctx.message.author.name)

        else:
            raise commands.ChannelNotFound("")

    @qr.error
    async def qr_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await ctx.message.author.send(
                f"Sorry, you cannot use this command yet, since you are not a scholar."
            )
        elif isinstance(error, commands.ChannelNotFound):
            channel = discord.utils.get(ctx.guild.channels, name=config['COMMANDS']['QR']['CHANNEL'])
            channel_id = channel.id
            await ctx.message.author.send(
                f"You used this command in the wrong channel. You can use it in the <#{channel_id}> channel."
            )
        elif isinstance(error, commands.MemberNotFound):
            print("This user was not found in the database : " + ctx.message.author.name)
            print("Current time : ", datetime.now().strftime("%H:%M:%S"))
            await ctx.message.author.send(
                f"Sorry, your Discord name could not be found in our database. Please contact a manager."
            )
        else:
            await ctx.message.author.send(
                f"Something went wrong when invoking the _{ctx.command.name}_ command... The managers have been notified of this problem."
            )
            channel = discord.utils.get(ctx.guild.channels, name=config['ERROR']['CHANNEL'])
            await channel.send(
                f"""Unhandled error in {ctx.message.channel.mention}. Exception caused by **{ctx.message.author.name}#{ctx.message.author.discriminator}** while invoking the _{ctx.command.name}_ command.
                \nUser message: `{ctx.message.content}` ```{traceback.format_exc()}```"""
            )

        # Delete this message, to remove clutter
        login_channel = discord.utils.get(ctx.guild.channels, name=config['COMMANDS']['QR']['CHANNEL'])
        if login_channel != ctx.channel:
            await ctx.message.delete()


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

    signature = signedMessage["signature"].hex()

    # This is necessary according to discord guy
    if signature[-2:] == "1c":
        signature = signature[:-2] + "01"
    elif signature[-2:] == "1b":
        signature = signature[:-2] + "00"

    # Remplace in that example to the actual signed message
    requestBody["variables"]["input"]["signature"] = signature
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


def getScholar(scholarName):
    """Simple function to read the "Scholars" worksheet and return the dataframe"""

    # Open Scholars worksheet
    ws = gc.open("Scholars").worksheet("Scholars")

    # Convert to DataFrames
    df = gd.get_as_dataframe(ws).dropna(axis=0, how="all").dropna(axis=1, how="all")

    # Make everything lowercase
    df["Scholar Name"] = df["Scholar Name"].str.lower()

    # Find row corresponding with discord name
    row = df.loc[df["Scholar Name"] == scholarName.lower()]

    # Check if this discord ID exists
    try:
        # Return list of most important info
        return [row["Address"].tolist()[0], row["Info"].tolist()[0]]

    except Exception as e:
        print("Error with discord user: " + str(scholarName))

        # Return nothing
        return None


def setup(bot):
    bot.add_cog(QR(bot))
