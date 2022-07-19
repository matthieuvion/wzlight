
# wzlight

[![MIT License](https://img.shields.io/apm/l/atomic-design-ui.svg?)](https://github.com/tterb/atomic-design-ui/blob/master/LICENSEs)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)


`wzlight` is an asynchronous Python wrapper for the Call of Duty API
that focuses on Warzone endpoints.

## Features

- Asynchronous with help of HTTPX, the HTTP client library
- Light : only centered around the few GET methods to collect Warzone stats
- Handle SSO auth. the (now) only available way to connect to the API

## Installation

```bash
  # with pip
  pip install wzlight
```
```bash
  # with Poetry
  poetry add wzlight
```

    
## Client usage

```python
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

    # Initially httpx.AsyncClient) was built in its own cls, but letting users define it at app-level --as a context manager,
    # ensures more robustness and flexibility (custom timeout, limits...) and prevent async loop event errors.
    # Thus, your main() should follow the preferred approach while working with an async http client:

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

``` 
#### Focus : example of a concurrent run

```python

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

    api = Api(sso)

    # We're running concurrently on match details endpoint, given a list of matchIds
    # COD API is unofficial and undocumented, rate limits / restrictions are not known
    # So you should probably --at least, handle some concurrency limits e.g for fetching a batch of matchs
    # See. httpx.Limits, async.Semaphore or other librairies such as aiometer


    matchIds = [
        5850171651963062771,
        6910618934945378397,
        16975576559940046894,
        639235311963231866,
        11887968911271282782,
        7897970481732864368,
    ]

    # enclose api.getMatch into safe_GetMatch that adds a Semaphore threshold

    limit = asyncio.Semaphore(2)

    async def safe_GetMatch(httpxClient, platform, matchId):
        # No more than two concurrent tasks. If reaches two, wait 1 sec
        async with limit:
            r = await api.GetMatch(httpxClient, platform, matchId)
        if limit.locked():
            print("Concurrency limit reached, waiting ...")
            await asyncio.sleep(1)

    # Do not forget to open Client as context manager :
    async with httpx.AsyncClient() as httpxClient:

        tasks = []
        for matchId in matchIds:
            tasks.append(safe_GetMatch(httpxClient, platform, matchId))
        await asyncio.gather(*tasks)
        print(len(tasks))


if __name__ == "__main__":
    asyncio.run(main())
```

## Acknowledgements
![Love](https://img.shields.io/badge/Love-pink?style=flat-square&logo=data:image/svg%2bxml;base64,PHN2ZyByb2xlPSJpbWciIHZpZXdCb3g9IjAgMCAyNCAyNCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48dGl0bGU+R2l0SHViIFNwb25zb3JzIGljb248L3RpdGxlPjxwYXRoIGQ9Ik0xNy42MjUgMS40OTljLTIuMzIgMC00LjM1NCAxLjIwMy01LjYyNSAzLjAzLTEuMjcxLTEuODI3LTMuMzA1LTMuMDMtNS42MjUtMy4wM0MzLjEyOSAxLjQ5OSAwIDQuMjUzIDAgOC4yNDljMCA0LjI3NSAzLjA2OCA3Ljg0NyA1LjgyOCAxMC4yMjdhMzMuMTQgMzMuMTQgMCAwIDAgNS42MTYgMy44NzZsLjAyOC4wMTcuMDA4LjAwMy0uMDAxLjAwM2MuMTYzLjA4NS4zNDIuMTI2LjUyMS4xMjUuMTc5LjAwMS4zNTgtLjA0MS41MjEtLjEyNWwtLjAwMS0uMDAzLjAwOC0uMDAzLjAyOC0uMDE3YTMzLjE0IDMzLjE0IDAgMCAwIDUuNjE2LTMuODc2QzIwLjkzMiAxNi4wOTYgMjQgMTIuNTI0IDI0IDguMjQ5YzAtMy45OTYtMy4xMjktNi43NS02LjM3NS02Ljc1em0tLjkxOSAxNS4yNzVhMzAuNzY2IDMwLjc2NiAwIDAgMS00LjcwMyAzLjMxNmwtLjAwNC0uMDAyLS4wMDQuMDAyYTMwLjk1NSAzMC45NTUgMCAwIDEtNC43MDMtMy4zMTZjLTIuNjc3LTIuMzA3LTUuMDQ3LTUuMjk4LTUuMDQ3LTguNTIzIDAtMi43NTQgMi4xMjEtNC41IDQuMTI1LTQuNSAyLjA2IDAgMy45MTQgMS40NzkgNC41NDQgMy42ODQuMTQzLjQ5NS41OTYuNzk3IDEuMDg2Ljc5Ni40OS4wMDEuOTQzLS4zMDIgMS4wODUtLjc5Ni42My0yLjIwNSAyLjQ4NC0zLjY4NCA0LjU0NC0zLjY4NCAyLjAwNCAwIDQuMTI1IDEuNzQ2IDQuMTI1IDQuNSAwIDMuMjI1LTIuMzcgNi4yMTYtNS4wNDggOC41MjN6Ii8+PC9zdmc+)  
Inspiration (heavily) came from :  
Also check those links if your need documentation on how the API works
 - [EthanC/CallofDuty.py](https://github.com/EthanC/CallofDuty.py) : the most complete but now slightly deprecated (mainly the Auth.), async COD client (lot of exploited endpoints and methods + more than WZ) 
 - [Lierrmm/Node-CallOfDuty](https://github.com/Lierrmm/Node-CallOfDuty) : very clean async. wrapper written in NodeJS. Also check their Discord to get a grip on API subtleties and unofficial changes (privacy changes, rate limits etc)
 - [valtov/WarzoneStats](https://github.com/valtov/WarzoneStats) : very clean synch. Python wrapper by the creator of wzstats.gg

## License

[MIT](https://choosealicense.com/licenses/mit/)
