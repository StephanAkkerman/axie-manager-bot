import pandas as pd
import gspread
import gspread_dataframe as gd

gc = gspread.service_account(filename="authentication.json")


def getScholar(discordID):
    """ Simple function to read the "Scholars" worksheet and return the dataframe """

    # Open Scholar Stats and read the Scholars worksheet
    # For more info on how to set this up check out my other repos https://github.com/stephanAkkerman/
    ws = gc.open("Scholar Stats").worksheet("Scholars")

    # Convert to DataFrames
    df = gd.get_as_dataframe(ws).dropna(axis=0, how="all").dropna(axis=1, how="all")

    # Find row corresponding with discordID
    row = df.loc[df["Discord ID"] == discordID]

    # Check if this discord ID excists
    try:
        # Return list of most important info
        return [row["Address"].tolist()[0], row["Info"].tolist()[0]]

    except Exception as e:
        print("Error with discord user: " + str(discordID))

        # Return nothing
        return None


# Put Your Discord Bot Token Here
TOKEN = "Your Discord bot token"

KEY = "Your fernet encryption / decryption key"

GUILD = "Your Guild Name"
