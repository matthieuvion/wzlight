from enum import Enum


class Platforms(Enum):
    PSN = "psn"
    XBOX = "xbl"
    BATTLENET = "battle"
    ACTIVISION = "acti"
    UNO = "uno"


class Endpoints(Enum):

    # Username's profile lifetime stats
    profile = "/stats/cod/v1/title/mw/platform/{platform}/{endpointType}/{username}/profile/type/wz"

    # 20 most recent matches of given username, with username/teammates stats for every match (no other players)
    recentMatches = "/crm/cod/v2/title/mw/platform/{platform}/{endpointType}/{username}/matches/wz/start/0/end/0/details"

    # Returns (up to) 20 recent matches, specifying end/start times
    recentMatchesWithDate = "/crm/cod/v2/title/mw/platform/{platform}/{endpointType}/{username}/matches/wz/start/{startTimestamp}/end/{endTimestamp}/details"

    # Returns 1000 recent matches, with only the timestamps, matchIds, mapId, and platform
    matches = "/crm/cod/v2/title/mw/platform/{platform}/{endpointType}/{username}/matches/wz/start/0/end/0"

    # Returns up to 1000 recent matches between dates, with only the timestamps, matchIds, mapId, and platform
    matchesWithDate = "/crm/cod/v2/title/mw/platform/{platform}/{endpointType}/{username}/matches/wz/start/{startTimestamp}/end/{endTimestamp}"

    # Returns the details of the specific match for each player of this match
    match = "/crm/cod/v2/title/mw/platform/{platform}/fullMatch/wz/{matchId}/en"
