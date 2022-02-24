##> Imports
# > 3rd party dependencies
import aiohttp
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_fixed

# > Local dependencies
from alerts.graphql import *


@retry(stop=stop_after_attempt(12), wait=wait_fixed(5))
async def api_genes(ids: str):
    """Gets a string of ids and returns the raw response"""

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.axie.technology/getgenes/" + ids + "/all"
        ) as r:
            response = await r.json()

            if type(response) is dict:
                if "message" in response.keys():
                    raise Exception("Stupid Genes API")

            return response


@retry(stop=stop_after_attempt(12), wait=wait_fixed(5))
async def api_new_listings():
    """Gets the new listings on the market and returns it as a pandas dataframe"""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url,
            json={
                "query": axie_query,
                "operationName": axie_operationName,
                "variables": axie_variables,
            },
        ) as r:
            response = await r.json()
            # Make it a dataframe and specify the important columns
            return pd.DataFrame(response["data"]["axies"]["results"])[
                [
                    "id",
                    "auction",
                    "class",
                    "stage",
                    "breedCount",
                    "parts",
                    "image",
                    "stats",
                ]
            ]


@retry(stop=stop_after_attempt(12), wait=wait_fixed(5))
async def api_old_listings(
    from_var, classes, breedCount, parts, hp, speed, skill, morale
):
    """Gets the old listings on the market and returns it as a pandas dataframe"""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url,
            json={
                "query": old_axies_query,
                "operationName": old_axie_operationName,
                "variables": old_axie_variables(
                    from_var, classes, breedCount, parts, hp, speed, skill, morale
                ),
            },
        ) as r:
            response = await r.json()
            return pd.DataFrame(response["data"]["axies"]["results"])[
                ["id", "auction", "class", "breedCount", "parts", "image"]
            ]


@retry(stop=stop_after_attempt(12), wait=wait_fixed(5))
async def api_axie_details(id):
    """Gets details of specific axie id"""

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url,
            json={
                "query": details_query,
                "operationName": "GetAxieDetail",
                "variables": {"axieId": id},
            },
        ) as r:
            response = await r.json()
            df = pd.DataFrame.from_dict(response["data"]["axie"], orient="index")
            df = df.transpose()
            return df[
                [
                    "id",
                    "image",
                    "class",
                    "stage",
                    "breedCount",
                    "level",
                    "parts",
                    "stats",
                    "auction",
                ]
            ]


@retry(stop=stop_after_attempt(12), wait=wait_fixed(5))
async def api_game_api(ids):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://game-api.axie.technology/api/v1/" + ids) as r:
            response = await r.json()
            return pd.DataFrame(response).transpose()


@retry(stop=stop_after_attempt(12), wait=wait_fixed(5))
async def api_game_api_single(id):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://game-api.axie.technology/api/v1/" + id) as r:
            response = await r.json()
            return pd.DataFrame([response])


@retry(stop=stop_after_attempt(12), wait=wait_fixed(5))
async def api_owner_axies(address):
    """
    Gets axies of specific Ronin address
    Returns a dataframe consisting of columns "id", "auction", "class", "breedCount", "parts", "image", "price"
    """

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://axieinfinity.com/graphql-server-v2/graphql",
            json={
                "query": "query GetAxieBriefList($auctionType: AuctionType, $criteria: AxieSearchCriteria, $from: Int, $sort: SortBy, $size: Int, $owner: String) {\n  axies(auctionType: $auctionType, criteria: $criteria, from: $from, sort: $sort, size: $size, owner: $owner) {\n    total\n    results {\n      ...AxieBrief\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment AxieBrief on Axie {\n  id\n  name\n  stage\n  class\n  breedCount\n  image\n  title\n  battleInfo {\n    banned\n    __typename\n  }\n  auction {\n    currentPrice\n    currentPriceUSD\n    __typename\n  }\n  parts {\n    id\n    name\n    class\n    type\n    specialGenes\n    __typename\n  }\n  __typename\n}\n",
                "operationName": "GetAxieBriefList",
                "variables": {"owner": address},
            },
        ) as r:
            response = await r.json()
            return pd.DataFrame(response["data"]["axies"]["results"])


@retry(stop=stop_after_attempt(12), wait=wait_fixed(5))
async def api_eth_price():
    """
    Gets the current ethereum exchange rate
    """

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://graphql-gateway.axieinfinity.com/graphql",
            json={
                "query": "query NewEthExchangeRate {\n  exchangeRate {\n    eth {\n      usd\n      __typename\n    }\n    __typename\n  }\n}\n",
                "operationName": "NewEthExchangeRate",
            },
        ) as r:
            response = await r.json()
            return response["data"]["exchangeRate"]["eth"]["usd"]


@retry(stop=stop_after_attempt(12), wait=wait_fixed(5))
async def api_missions(ronin, token):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://game-api.axie.technology/missions/" + ronin,
            headers={"Authorization": "Bearer " + token},
        ) as r:
            response = await r.json()
            if response == {}:
                return None
            elif response["success"]:
                return response["items"][0]["missions"]
            else:
                raise Exception()
            
@retry(stop=stop_after_attempt(12), wait=wait_fixed(5))
async def api_PVP(ronin):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://game-api.axie.technology/logs/pvp/" + ronin) as r:
            response = await r.json()
            if response == {}:
                return None
            elif response["battles"]:
                return response["battles"]
            else:
                raise Exception()

@retry(stop=stop_after_attempt(12), wait=wait_fixed(5))
async def api_player(ronin, token):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://game-api.axie.technology/player/" + ronin,
            headers={"Authorization": "Bearer " + token},
        ) as r:
            response = await r.json()
            if response == {}:
                return None
            elif response["success"]:
                return response["player_stat"]
            else:
                raise Exception()
