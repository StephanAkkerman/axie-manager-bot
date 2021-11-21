# Axie Manager Bot
This is a Discord bot written in Python, with the purpose of helping our guild manage the scholars in our Discord server.
The purpose of this bot is that it can be used for guilds with multiple scholars and different managers, who each have their own scholars and wallets. 

## Features
### Commands
- `!qr`: Scholars can request their QR-code in the specified channel, default in '🤖┃login' channel. The bot will send them a private message containing their QR-code for login.
- `!mute` / `!unmute`: Mute and unmute specific users. Usage `!mute <@user>`, this gives a user the 'mute' role.
- `!encrypt`: Encrypt messages, necessary for encrypting private keys and storing them. Usage `!encrypt <message>`.
- `!tryouts`: Start tryouts, divides users with role 'tryout' in specific channels. More about this [below](#tryouts).
- `!announce`: Make announcements, using the bot as message sender. Usage `!announce <#channel>`, followed by a next `<text>`.
- `!clear`: Clear a number of messages. Usage `!clear <number>`, or `!clear <number> <@user>` to clear messages of specific user.
- `!manager`: Scholars can request information about their manager using this command. Only works if a scholar has manager assigned to them via a role.
- `!leaderboard`: Prints the leaderboard consisting of all scholars and ranked by MMR, also shows their average daily SLP income.
- `!scholar`: Adds a scholar to the database of scholars. Usage `!scholar <scholar_discord_id> <address> <split> <payout_address> <encrypted_key> <[manager]>`. See the example [below](#general) of how the values should look like.
- `!mydata`: Scholar can request their up to date data, consisting of: in game slp, MMR, rank, payout day, and the number of days untill payout day.
- `!help`: Custom written `!help` command.

### Automation
- Automated alerts of axies specified in a Google Spreadsheet. More about this [below](#alerts).
- Automated buy, sell and listing alerts of other managers. These get posted in '🤝┃axie-trades' channel.
- Automated error handling. This sends all errors that occur in the '🐞┃bot-errors' channel, so every manager in the server is aware if there are any issues.
- If a user gets the role 'scholar' then the bot will send them a video containing an explanation about how everything works.
- If a user gets the role 'tryout' then the bot will send them a video containing an explanation about how everything works.
- Users get the role 'verified' if the click the ✅ below an announcement.

### Tryouts
Tryouts are used to select a new scholar from a group of people (with the role 'tryout'). For each account that is available for a new scholar a new tryout group can be made, it is also possible to make less groups and pick the first and second best players.
Currenlty we let every tryout play for 3 hours on the account and after all tryouts are done the best will be picked. This is done by selecting the tryout that had the best winrate. At the moment the API for that is offline, so after a tryout is done they should send screenshots of their match history.

### Disclaimer
The code for the `!qr` command was inspired by [ZracheSs | xyZ](https://github.com/ZracheSs-xyZ), check out their repo for the original code.

## Dependencies
The required packages to run this code can be found in the `requirements.txt` file. To run this file, execute the following code block:
```
$ pip install -r requirements.txt 
```
Alternatively, you can install the required packages manually like this:
```
$ pip install <package>
```

## Setup
### Making a Discord bot
- Setup your own Discord bot, following this [tutorial](https://realpython.com/how-to-make-a-discord-bot-python/).
- Give the bot admin rights and all permissions possible, since this is the easiest way to set it up.
- Invite the bot to your server.
- Write down the token of the bot, as this will be used later.

Optional:\
Make a nice avatar for the bot.

### Mandatory Channels
As mentioned above there are some channels, with specific channel names necessary. These channels are listed below.
- `🤖┃login`: In this channel scholars should request their QR-code, using the `!qr` command.
- `💎┃bot-alerts`: In this channel axies will be automatically posted, see [alerts](#alerts) for more info.
- `🤝┃axie-trades`: In this channel the buy, sell and listing alerts of managers will be posted.
- `🐞┃bot-errors`: In this channel issues with the command will be posted.

### Spreadsheet (Database)
This part needs to be done, otherwise more than half of the functions of this bot will not work. This spreadsheet will serve as a simple database that everyone manager can access. 
- Go to Google Drive and make a new spreadsheet named 'Scholars'.
- Name the worksheet also 'Scholars', please do not deviate from this.
- Make a table that looks like this:
![Scholars](https://github.com/StephanAkkerman/Axie_Manager_Bot/blob/main/img/scholars.png)
- Fill in the values manually or using the `!scholar` command.
- Give the bot access to your spreadsheet by following these [instructions](https://docs.gspread.org/en/latest/oauth2.html#for-bots-using-service-account)
- Save your authentication.json file that you got from the above instructions.

Note:\
Share your Scholar spreadsheet with the email provided in the .json file. This email is shown after `"client_email":`.

### Encryption
If you want to use the `!encrypt` function, you should have a fernet key. To generate this key use the following code:
```py
from cryptography.fernet import Fernet
print(Fernet.generate_key())
```
Write down the key and go to the [next section](#authentication.json).

### Authentication.json
This file is automatically generated and necessary for the Python gspread library. This will also function as the file for storing all the other 'secret' variables. The following variables should be add to this json file. Do not change any of the other stuff that is already in there. Do not forget to add an extra comma after each new line.
- `"TOKEN" : <Your Discord bot token>`
- `"GUILD" : <Name of the Discord server that the bot should join>`
- `"KEY" : <Your Fernet encryption / decryption key>`

### Alerts
For this part we are using Google Spreadsheets again, so that every manager can easily make adjustments to it.
- Make a new spreadsheet named 'Axie Builds' and name the worksheet 'main'.
- Make a table that looks like this:
![Builds](https://github.com/StephanAkkerman/Axie_Manager_Bot/blob/main/img/builds.png)
- Filling in a discord name will tag that Discord user if an alert for that build happens.

Note:\
These are old builds in the table, search for a axie build that works well with the currenta meta.

## How to run
- Clone the repository and install dependencies as specified [above](#dependencies).
- Follow the steps mentioned in [setup](#setup)
- Run `$ python src/main.py`
- See result
