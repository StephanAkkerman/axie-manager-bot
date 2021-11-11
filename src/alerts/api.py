# 3rd party dependencies
import aiohttp
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_fixed

# Local dependencies
from alerts.graphql import *

@retry(stop=stop_after_attempt(12), wait=wait_fixed(5))
async def api_genes(ids:str):
    """ Gets a string of ids and returns the raw response """

    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.axie.technology/getgenes/" + ids + "/all") as r:
            return await r.json()

@retry(stop=stop_after_attempt(12), wait=wait_fixed(5))
async def api_new_listings():
    """ Gets the new listings on the market and returns it as a pandas dataframe"""
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
            return pd.DataFrame(response["data"]["axies"]["results"])[["id","auction","class","stage","breedCount","parts","image","stats",]]

@retry(stop=stop_after_attempt(12), wait=wait_fixed(5))
async def api_old_listings(from_var, classes, breedCount, parts):
    """ Gets the old listings on the market and returns it as a pandas dataframe"""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url,
            json={
                "query": old_axies_query,
                "operationName": old_axie_operationName,
                "variables": old_axie_variables(
                    from_var, classes, breedCount, parts
                ),
            },
        ) as r:
            response = await r.json()
            return pd.DataFrame(response["data"]["axies"]["results"])[["id", "auction", "class", "breedCount", "parts", "image"]]