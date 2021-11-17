##> Imports
# > Standard library
import requests

# > 3rd party dependencies
import gspread
import gspread_dataframe as gd


def get_parts(axie_id, specify):
    response = requests.get(
        "https://api.axie.technology/getgenes/" + str(int(axie_id))
    ).json()

    partNames = []
    partIds = []

    # Count deviations for every part
    for part in ["mouth", "horn", "back", "tail"]:
        partIds.append(response[part]["d"]["partId"])
        partNames.append(response[part]["d"]["name"])

    if specify == "Names":
        return partNames
    else:
        return partIds


def get_builds():
    """Simple function to read the "Axie Builds" spreadsheet and return the dataframe"""

    gc = gspread.service_account(filename="authentication.json")

    ws = gc.open("Axie Builds").worksheet("main")
    builds = gd.get_as_dataframe(ws).dropna(axis=0, how="all").dropna(axis=1, how="all")

    # Make class and parts a list
    # Split class at , + space
    builds["Class"] = builds["Class"].str.split(", ")

    builds["Parts"] = builds["Parts (Axie ID)"].apply(get_parts, args=("Names",))

    builds["Part Ids"] = builds["Parts (Axie ID)"].apply(get_parts, args=("Ids",))

    if "Discord Name" in builds.index:
        builds["Discord Name"] = builds["Discord Name"].str.split(", ")

    # Convert it to list of dictionaries
    return builds.to_dict(orient="records")
