# Axie Manager Bot
This is a simple python bot, with the purpose of helping our guild manage the scholars in our Discord server.
The purpose of this bot is that it can be used for guilds with multiple scholars, who each have their own scholars and wallets. 

## QR Code
The code of QRCodeBot.py and part of main.py was written by [ZracheSs | xyZ](https://github.com/ZracheSs-xyZ), check out their repo for the original code.

## Features
- Send qr code if a scholar types !qr in the 🤖┃login channel
- Encrypt private keys using your own fernet key, for extra protection
- Give new scholars automatically a role, currently disabled

## Dependencies
The required packages to run this code can be found in the `requirements.txt` file. To run this file, execute the following code block:
```
$ pip install -r requirements.txt 
```
Alternatively, you can install the required packages manually like this:
```
$ pip install <package>
```

## How to run
- Clone the repository
- Optional: Setup your own Discord bot, following this [tutorial](https://realpython.com/how-to-make-a-discord-bot-python/)
- Add your Discord bot token and your server name to the secret file
- Add your fernet key to the secret file
- Setup [Scholar Stats](https://github.com/StephanAkkerman/Scholar_Stats), so that the data can be read from Google spreadsheets
- Run `$ python src/main.py`
- See result
