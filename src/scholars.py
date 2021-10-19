import pandas as pd
import gspread
import gspread_dataframe as gd

gc = gspread.service_account(filename="authentication.json")


def getScholar(discordID):
    """Simple function to read the "Scholars" worksheet and return the dataframe"""

    # Open Scholars worksheet
    ws = gc.open("Scholar Stats").worksheet("Scholars")
    ws2 = gc.open("Scholar Stats Winston").worksheet("Scholars")

    # Convert to DataFrames
    df = gd.get_as_dataframe(ws).dropna(axis=0, how="all").dropna(axis=1, how="all")
    df = df.append(
        gd.get_as_dataframe(ws2).dropna(axis=0, how="all").dropna(axis=1, how="all")
    )

    # Find row corresponding with discordID
    row = df.loc[df["Discord ID"] == discordID]

    # Check if this discord ID exists
    try:
        # Return list of most important info
        return [row["Address"].tolist()[0], row["Info"].tolist()[0]]

    except Exception as e:
        print("Error with discord user: " + str(discordID))

        # Return nothing
        return None
