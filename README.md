# Axie Manager Bot
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![MIT License](https://img.shields.io/github/license/StephanAkkerman/Axie_Manager_Bot.svg?color=brightgreen)](https://opensource.org/licenses/MIT)

---

This is a Discord bot written in Python, with the purpose of helping our guild manage the scholars in our Discord server.
The purpose of this bot is that it can be used for guilds with multiple scholars and different managers, who each have their own scholars and wallets.

## Features
This bot was made with configurability in mind, meaning that every feature listed below can be turned on or off, and be changed easily. If you do not want a feature, just turn it off, all automation and listeners works for your custom roles and channels, so be sure to check out the settings in config_example.yaml and change them to your liking!

### Commands
- `!announce`: Make announcements, using the bot as message sender. Usage `!announce <#channel>`, followed by a next `<text>`.
- `!clear`: Clear a number of messages. Usage `!clear <number>`, or `!clear <number> <@user>` to clear messages of specific user.
- `!encrypt`: Encrypt messages, necessary for encrypting private keys and storing them, using your personal uniquely generated encryption key. Usage `!encrypt <message>`.
- `!funds`: For managers to add their funds account address to the database. Usage `!funds <ronin address>`.
- `!help`: Custom written `!help` command.
- `!issue`: Make a new issue for this bot or any other public GitHub repository. Usage `!issue <title>` followed by the description and labels. Needs your personal GitHub token to work, so this is disabled by default.
- `!manager`: Scholars can request information about their manager using this command. Great if there are multiple managers in one server.
- `!mute` / `!unmute`: Mute and unmute specific users. Usage `!mute <@user>`, this gives a user the 'mute' role.
- `!mydata`: Scholar can request their up to date data, consisting of: in game slp, MMR, rank, payout day, and the number of days untill payout day.
- `!price`: Request suggested prices for selling your axie. Usage `!price <axie ID>`, gives maximum 4 different prices based on different criteria.
- `!scholar`: Adds a scholar to the database of scholars. Usage `!scholar <scholar_discord_name> <address> <split> <payout_address> <encrypted_key> <[manager]>`. See the example [below](#spreadsheet) of how the values should look like.
- `!tryout`: Start tryouts, divides users with role 'tryout' in specific channels. More about this [below](#tryouts).
- `!qr`: Scholars can request their QR-code in a dedicated channel. The bot will send them a private message containing their QR-code for login.

### Automation
In config_example.yaml this is also called 'Loops', you can customize each channel that these automated messages will get send in.

- Axie Alert: Automated alerts of axies specified in a Google Spreadsheet. More about this [below](#alerts).
- Axie Trades: Automated buy, sell and listing alerts of other managers.
- Clean Channel: The channel specified will get cleaned every x hours, useful if a channel is full with messages often.
- Instagram: If you have a Instagram account that you want server users to be aware of. This will send every new post in the dedicated channel.
- Leaderboard: Every 4 hours an updated leaderboard gets posted in the dedicated channel, showing the top performing scholars ranked by MMR.
- Prices: Every 4 hours the new SLP, AXS, ETH, and Axie floor prices get posted in the dedicated channel.
- SLP Warning: 1 hour before the daily reset scholars get mentioned if they have not yet completed all quests or are below 800 MMR.

### Listeners
This section is about the other type of automation, which is based on events. 

- On Command: If a user uses a bot command it will get shown in the console.
- On Member Join: If a new user joins the server they will get a specific role, disabled by default.
- On Member Update: 
  - If a user gets the role 'scholar' then the bot will send them a video containing an explanation about how everything works.
  - If a user gets the role 'tryout' then the bot will send them a video containing an explanation about how everything works.
- On Message: Deletes all messages in specific channel that are not send by the bot (by using the `!announcement` command).
- On Raw Reaction Add: 
  - If you react using the 💎 emoji below an axie alert, you will be the only one able to view this axie.
  - Users get the role 'verified' if the click the ✅ below an announcement.
- Translate: Automatically translates certain languages to another language based on your preferences. For instance from Tagalog to English, the translated messages will be send to a dedicated channel to remove clutter.

### Tryouts
Tryouts are used to select a new scholar from a group of people (with the role 'tryout'). For each account that is available for a new scholar a new tryout group can be made, it is also possible to make less groups and pick the first and second best players.
Currently we let every tryout play for 3 hours on the account and after all tryouts are done the best will be picked. This is done by selecting the tryout that had the best winrate. At the moment the API for that is offline, so after a tryout is done they should send screenshots of their match history.

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
This part is about creating the Discord bot, setting up the basics, and inviting it to your server. For the first part you can watch this [video (watch until 2:20)](https://www.youtube.com/watch?v=Pbq7vPsHDtc).

Or follow these written instructions:
- Setup your own Discord bot, following this [written tutorial](https://realpython.com/how-to-make-a-discord-bot-python/) or this 
- Give the bot admin rights and all permissions possible, since this is the easiest way to set it up.
- Invite the bot to your server.

Then you need to add the custom emojis to the server (can be skipped).
- Download the custom emoji pictures [here](https://github.com/StephanAkkerman/Axie_Manager_Bot/tree/main/img/emojis).
- Add them to your server ([instructions](https://support.discord.com/hc/en-us/articles/360036479811-Custom-Emojis)).

Last you need to fill in the important information in `config_example.yaml`, so the bot knows which server it should be connected to.
- Open `config_example.yaml` 
- Write your bot token behind `TOKEN:` (line 2)
- Write your server name behind `GUILD_NAME:` (line 3)
- If you changed the custom emoji names, change them in the file too (line 37, 40, 41).

### Spreadsheet
This part needs to be done and is a bit technical, so follow the steps carefully. Or follow the instructions from this (starts from 1:58) [video](https://youtu.be/6zeDGeGGHx4?t=118)

If you prefer written instructions follow the instructions below:
- Enable API access for the new project [instructions](https://docs.gspread.org/en/latest/oauth2.html#enable-api-access-for-a-project).
- Creating the `authentication.json file` [instructions](https://docs.gspread.org/en/latest/oauth2.html#for-bots-using-service-account).

After follow the instructions above, last things you need to do is this:
- Save your `authentication.json` file in the same folder as you saved the files for this bot.
- Make a new folder in your Google Drive and share it (by right clicking on it and pressing share) with the email provided in the `authentication.json` file, give this email editor rights. The email is shown after `"client_email":`, on line 6. The email should look like: `servicename@projectname.iam.gserviceaccount.com`. 

### Make the roles, channels, and spreadsheets
Because no one likes to go through the process of making all the new channels, roles, and spreadsheets themselves I have written a script to do it for you.
To run it you need to have followed the steps above, so you should have installed the dependencies, made the bot, and gave it access to your preferred Google Drive folder. If you have done all that you can execute the following code:
```
python src/setup.py
```
This will also rename `config_example.yaml` to just `config.yaml` so you do not need to worry about renaming that as well. After that is done you are ready for deploying the bot.

### Alerts
As you might have noticed the bot created a spreadsheet called Axie Alerts. This spreadsheet specifies the Axies that should be alerted in the server, for instance if they have a low price or good genes. Below an example is shown of how you can fill in this spreadsheet.
![builds](https://github.com/StephanAkkerman/Axie_Manager_Bot/blob/main/img/builds.png)

Example of an alert that the bot automatically sends:\
![alert](https://github.com/StephanAkkerman/Axie_Manager_Bot/blob/main/img/alert.png)

## How to run
- Clone the repository and install dependencies as specified [above](#dependencies).
- Follow the steps mentioned in [setup](#setup).
- Run `$ python src/main.py`
- Add your scholars using the `!scholar <scholar_discord_name> <address> <split> <payout_address> <encrypted_key> <[manager]>` command. 
- Give your users their dedicated roles.
- See the results.
