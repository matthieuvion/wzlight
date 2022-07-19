import os
import asyncio
from pprint import pprint

import httpx
from dotenv import load_dotenv

from wzlight import Api


async def main():

    load_dotenv()
    sso = os.environ["SSO"]
    username = "amadevs#1689"
    platform = "battle"

    # Initialize Api with a SSO token
    # SSO token can be found in browser while login-in to callofduty.com

    api = Api(sso)

    # Wrapper internal methods are using the httpx async HTTP library

    # Initially a http client (httpx.AsyncClient) was built in its own cls, but letting users define it at app-level --as a context manager,
    # ensures more flexibility (custom timeout, limits...) and prevent async loop event errors.
    # Thus, your main() should follow the preferred approach while working with an async http client such as:

    async with httpx.AsyncClient() as httpxClient:

        profile = await api.GetProfile(httpxClient, platform, username)
        pprint(profile, depth=2)

        recent_matches = await api.GetRecentMatches(httpxClient, platform, username)
        recent_matches_short = [match for match in recent_matches[:2]]
        pprint(recent_matches_short, depth=3)

        matchStats = await api.GetMatch(
            httpxClient, platform, matchId=11378702801403672847
        )
        pprint(matchStats, depth=1)


if __name__ == "__main__":
    asyncio.run(main())
