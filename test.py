import os
import asyncio
from pprint import pprint

from dotenv import load_dotenv

from wzlight import Api


async def main():

    load_dotenv()
    sso = os.environ["SSO"]
    username = "amadevs#1689"
    platform = "battle"

    # Initialize Api/client httpx.session
    # SSO value can be found inspecting your browser while logging-in to callofduty.com

    api = Api(sso)

    # Get a player's profile

    profile = await api.GetProfile(platform, username)
    pprint(profile, depth=2)

    # Get last 20 recent matches
    # Another client method allows to specify start/end timestamsps

    recent_matches = await api.GetRecentMatches(platform, username)
    recent_matches_short = [match for match in recent_matches[:2]]
    pprint(recent_matches_short, depth=3)

    # Get 1000 last played matchId, platform, matchType (id), timestamp

    matches = await api.GetMatches(platform, username)
    matches_short = [match for match in matches[:5]]
    pprint(matches_short)

    # Get detailed stats about a match, given a matchId

    match_details = await api.GetMatch(platform, matchId=3196515799358056305)
    match_details_short = [player for player in match_details[:2]]
    pprint(match_details_short, depth=3)

    # Example on how to run *concurrently* passing a list of matchId

    limit = asyncio.Semaphore(2)

    async def safe_GetMatch(platform, matchId):
        # no more than two concurrent tasks
        async with limit:
            r = await api.GetMatch(platform, matchId)
        if limit.locked():
            print("Concurrency limit reached, waiting ...")
            await asyncio.sleep(1)

    matchIds = [
        11378702801403672847,
        18088202254080399946,
        5850171651963062771,
        6910618934945378397,
        16975576559940046894,
        639235311963231866,
        11887968911271282782,
        7897970481732864368,
    ]

    tasks = []
    for matchId in matchIds:
        tasks.append(safe_GetMatch(platform, matchId))
    await asyncio.gather(*tasks)
    print(len(tasks))


if __name__ == "__main__":
    asyncio.run(main())
