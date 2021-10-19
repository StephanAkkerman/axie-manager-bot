# ===============
# === GRAPHQL ===
# ===============

# Axie GraphQL endpoint
url = "https://axieinfinity.com/graphql-server-v2/graphql"

# GraphQL request query
axie_operationName = "GetAxieLatest"

# Get the latest axies being sold
# Don't get the eggs, max size is 100
axie_variables = """
{
  "from": 0,
  "size": 100,
  "sort": "Latest",
  "auctionType": "Sale",
  "criteria": {"stages":[4]}
}
"""

# Get all the information about these axies
axie_query = """
query GetAxieLatest($auctionType: AuctionType, $criteria: AxieSearchCriteria, $from: Int, $sort: SortBy, $size: Int, $owner: String) 
{
  axies(auctionType: $auctionType, criteria: $criteria, from: $from, sort: $sort, size: $size, owner: $owner) 
  {
    total
    results 
    {
      ...AxieRowData
      __typename
    }
    __typename
  }
}

fragment AxieRowData on Axie
{
  id
  image
  class
  name
  genes
  owner
  class
  stage
  title
  breedCount
  level
  parts {
    ...AxiePart
    __typename
  }
  stats {
    ...AxieStats
    __typename
  }
  auction {
    ...AxieAuction
    __typename
  }
  __typename
}

fragment AxiePart on AxiePart {
  id
  name
  class
  type
  specialGenes
  stage
  abilities {
    ...AxieCardAbility
    __typename
  }
  __typename
}

fragment AxieCardAbility on AxieCardAbility {
  id
  name
  attack
  defense
  energy
  description
  backgroundUrl
  effectIconUrl
  __typename
}

fragment AxieStats on AxieStats {
  hp
  speed
  skill
  morale
  __typename
}

fragment AxieAuction on Auction {
  startingPrice
  endingPrice
  startingTimestamp
  endingTimestamp
  duration
  timeLeft
  currentPrice
  currentPriceUSD
  suggestedPrice
  seller
  listingIndex
  state
  __typename
}
"""

# Old axie listings
old_axie_operationName = "GetAxieBriefList"


def old_axie_variables(from_var, classes, breedCount, parts):
    return f"""
  {{
      "from": {from_var},
      "size": 100,
      "sort": "PriceAsc",
      "auctionType": "Sale",
      "criteria": {{"classes":{classes}, "stages":[4], "breedCount":{breedCount}, "parts":{parts}}}
  }}
  """


old_axies_query = """
query GetAxieBriefList(
  $auctionType: AuctionType
  $criteria: AxieSearchCriteria
  $from: Int
  $sort: SortBy
  $size: Int
  $owner: String
) {
  axies(
    auctionType: $auctionType
    criteria: $criteria
    from: $from
    sort: $sort
    size: $size
    owner: $owner
  ) {
    total
    results {
      ...AxieBrief
      __typename
    }
    __typename
  }
}

fragment AxieBrief on Axie {
  id
  name
  stage
  class
  breedCount
  image
  title
  battleInfo {
    banned
    __typename
  }
  auction {
    currentPrice
    currentPriceUSD
    __typename
  }
  parts {
    id
    name
    class
    type
    specialGenes
    __typename
  }
  __typename
}
"""
