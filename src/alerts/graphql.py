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


def old_axie_variables(from_var, classes, breedCount, parts, hp, speed, skill, morale):
    return f"""
  {{
      "from": {from_var},
      "size": 100,
      "sort": "PriceAsc",
      "auctionType": "Sale",
      "criteria": {{"classes":{classes}, "stages":[4], "breedCount":{breedCount}, "parts":{parts}, "hp":{hp}, "speed":{speed}, "skill":{skill}, "morale":{morale}}}
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

details_query = "query GetAxieDetail($axieId: ID!) {\n  axie(axieId: $axieId) {\n    ...AxieDetail\n    __typename\n  }\n}\n\nfragment AxieDetail on Axie {\n  id\n  image\n  class\n  chain\n  name\n  genes\n  owner\n  birthDate\n  bodyShape\n  class\n  sireId\n  sireClass\n  matronId\n  matronClass\n  stage\n  title\n  breedCount\n  level\n  figure {\n    atlas\n    model\n    image\n    __typename\n  }\n  parts {\n    ...AxiePart\n    __typename\n  }\n  stats {\n    ...AxieStats\n    __typename\n  }\n  auction {\n    ...AxieAuction\n    __typename\n  }\n  ownerProfile {\n    name\n    __typename\n  }\n  battleInfo {\n    ...AxieBattleInfo\n    __typename\n  }\n  children {\n    id\n    name\n    class\n    image\n    title\n    stage\n    __typename\n  }\n  __typename\n}\n\nfragment AxieBattleInfo on AxieBattleInfo {\n  banned\n  banUntil\n  level\n  __typename\n}\n\nfragment AxiePart on AxiePart {\n  id\n  name\n  class\n  type\n  specialGenes\n  stage\n  abilities {\n    ...AxieCardAbility\n    __typename\n  }\n  __typename\n}\n\nfragment AxieCardAbility on AxieCardAbility {\n  id\n  name\n  attack\n  defense\n  energy\n  description\n  backgroundUrl\n  effectIconUrl\n  __typename\n}\n\nfragment AxieStats on AxieStats {\n  hp\n  speed\n  skill\n  morale\n  __typename\n}\n\nfragment AxieAuction on Auction {\n  startingPrice\n  endingPrice\n  startingTimestamp\n  endingTimestamp\n  duration\n  timeLeft\n  currentPrice\n  currentPriceUSD\n  suggestedPrice\n  seller\n  listingIndex\n  state\n  __typename\n}\n"
