# 3rd party dependencies
import pandas as pd
import aiohttp

# Local dependencies
from alerts.api import api_genes


async def get_genes(axie_df, r1, r2, get_auction_info=False):

    # Get all axie ids and add them together
    ids = ",".join(axie_df["id"].tolist())

    ret_axie_df = axie_df.copy()

    try:
        response = await api_genes(ids)
    except Exception as e:
        print(e)
        print("Error fetching api_genes")
        # Return an empty dataframe, so no crashes will occur
        return pd.DataFrame({})

    # Reponse returns columns ['cls', 'region', 'pattern', 'color', 'eyes', 'mouth', 'ears', 'horn', 'back', 'tail', 'axieId']
    if not get_auction_info:
        if type(response) == dict:
            df = pd.DataFrame.from_dict(response, orient="index")
            genes = df.transpose()
        else:
            genes = pd.DataFrame([pd.Series(value) for value in response])
    else:
        if len(axie_df) == 1:
            df = pd.DataFrame.from_dict(response, orient="index")
            genes = df.transpose()
        else:
            genes = pd.DataFrame(response)

    # Remove ids of axies that are currently in the API as eggs
    genes = genes.loc[~genes.story_id.isin(genes[genes.stage == 1]["story_id"].tolist())]

    # Add columns for parts
    for part in ["eyes", "ears", "mouth", "horn", "back", "tail"]:
        genes[part] = genes["traits"].apply(lambda x: x[part])

    # Count deviations for every part
    for part in ["mouth", "horn", "back", "tail"]:
        genes[f"{part} r1"] = [0 if x["d"] == x["r1"] else 1 for x in genes[part]]
        genes[f"{part} r2"] = [0 if x["d"] == x["r2"] else 1 for x in genes[part]]

    # Sum all the deviations
    genes["r1 deviation"] = (
        genes["mouth r1"] + genes["horn r1"] + genes["back r1"] + genes["tail r1"]
    )
    genes["r2 deviation"] = (
        genes["mouth r2"] + genes["horn r2"] + genes["back r2"] + genes["tail r2"]
    )

    # Only get the axies where deviations are lower than what we asked for
    genes = genes.loc[(genes["r1 deviation"] <= r1) & (genes["r2 deviation"] <= r2)]

    # Trim the axie_df based on ids in genes
    ret_axie_df = ret_axie_df.loc[axie_df["id"].isin(genes["story_id"].tolist())]

    # Add stats and auction info to axie_df, has the same order as axie_df
    if get_auction_info:
        ret_axie_df[
            [
                "stats",
                "auction",
                "eyes",
                "ears",
                "mouth",
                "horn",
                "back",
                "tail",
                "r1 deviation",
                "r2 deviation",
            ]
        ] = genes[
            [
                "stats",
                "auction",
                "eyes",
                "ears",
                "mouth",
                "horn",
                "back",
                "tail",
                "r1 deviation",
                "r2 deviation",
            ]
        ].to_numpy()
    else:
        # Do not add auction info to new_listing, since it already has that
        ret_axie_df[
            [
                "stats",
                "eyes",
                "ears",
                "mouth",
                "horn",
                "back",
                "tail",
                "r1 deviation",
                "r2 deviation",
            ]
        ] = genes[
            [
                "stats",
                "eyes",
                "ears",
                "mouth",
                "horn",
                "back",
                "tail",
                "r1 deviation",
                "r2 deviation",
            ]
        ].to_numpy()

    return ret_axie_df
