import requests
import pandas as pd


def get_genes(axie_df, r1, r2):

    # Get all axie ids and add them together
    ids = ",".join(axie_df["id"].tolist())

    try:
        response = requests.get("https://api.axie.technology/getgenes/" + ids).json()

    except Exception as e:
        print(e)
        print("Error at get_genes")

    # Reponse returns columns ['cls', 'region', 'pattern', 'color', 'eyes', 'mouth', 'ears', 'horn', 'back', 'tail', 'axieId']
    # Eyes and ears not important
    genes = pd.DataFrame(response)

    # Count deviations for every part
    for part in ["mouth", "horn", "back", "tail"]:
        if len(axie_df) == 1:
            # iloc[0] is d, r1 is [1], r2 is [2]
            genes[f"{part} r1"] = 0 if genes.iloc[0][part] == genes.iloc[1][part] else 1
            genes[f"{part} r2"] = 0 if genes.iloc[0][part] == genes.iloc[2][part] else 1

        else:
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

    # Get the corresponding ids
    ids = genes["axieId"].tolist()

    # Trim the axie_df based on those ids
    axie_df = axie_df.loc[axie_df["id"].isin(ids)]

    return axie_df
