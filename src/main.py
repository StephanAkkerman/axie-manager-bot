import os
import discord
import uuid
from SecretStorage import *
from QRCodeBot import *
from datetime import datetime
from cryptography.fernet import Fernet

# Set the client intents
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

# Get encryption key
fernet = Fernet(KEY)

# Todo
# bot = commands.Bot(command_prefix='!')
# Add @bot.command() instead of on_message


@client.event
async def on_ready():
    """ This gets printed on boot up"""

    guild = discord.utils.get(client.guilds, name=GUILD)
    print(
        f"{client.user} is connected to the following guild:\n"
        f"{guild.name}(id: {guild.id})"
    )


# @client.event
# async def on_member_join(member):
#    """ Gives new users the role Tryout """
#    role = discord.utils.get(member.guild.roles, name="Tryout")
#    await member.add_roles(role)

# QR code bot
@client.event
async def on_message(message):
    """ Listen for any incoming message """

    # If the author is the robot itself, then do nothing!
    if message.author == client.user:
        return

    # If the user writes !qr in the correct channel
    if message.channel.name == "🤖┃login":

        # Delete this message, to remove clutter
        await message.delete()

        # Do the rest if message is !qr
        if message.content == "!qr":

            # For logs
            current_time = datetime.now().strftime("%H:%M:%S")
            print("\n")

            # Get this scholars info from the sheet
            scholar_info = getScholar(message.author.id)

            # This for loop check for all the user's DiscordID in the Database
            if scholar_info != None:

                # Print log info
                print("This user received his QR Code : " + message.author.name)
                print("Discord ID : " + str(message.author.id))
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
                qrCodePath = f"QRCode_{message.author.id}_{str(uuid.uuid4())[0:8]}.png"
                qrcode.make(accessToken).save(qrCodePath)

                # Send the QrCode the the user who asked for it
                await message.author.send(
                    "------------------------------------------------\n\n\nHello "
                    + message.author.name
                    + "\nHere is your new QR Code to login : "
                )
                await message.author.send(file=discord.File(qrCodePath))
                # Delete picture
                os.remove(qrCodePath)
                return

            # Scholar does not exist in sheet, maybe different Discord ID?
            else:
                print("This user didn't receive a QR Code : " + message.author.name)
                print("Discord ID : " + str(message.author.id))
                print("Current time : ", current_time)
                return

        # Send feedback if it's not !qr
        else:
            await message.author.send(
                "Please only send '!qr' in the login channel channel!"
            )

    # ==================
    # === ENCRYPTION ===
    # ==================

    # If the user writes !encrypt followed by something else
    if message.channel.name == "🤖┃bots":
        if message.content.split()[0] == "!encrypt":

            # Error handling
            if len(message.content.split()) == 1:
                await message.author.send("Please type something after !encrypt")
                return

            # Delete this message, for privacy
            await message.delete()

            # Private key is send after !encrypt
            private_key = message.content.split()[1]

            # Encode private key
            encMessage = fernet.encrypt(private_key.encode())

            # Send a dm
            await message.author.send(
                "Hi "
                + message.author.name
                + ", here is your encrypted key:\n"
                + str(encMessage)
            )
            return


client.run(TOKEN)
