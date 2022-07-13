from enum import Enum
import requests

import httpx
import urllib.parse

from auth import Auth


class Api:
    baseUrl = "https://my.callofduty.com/api/papi-client"

    class Platforms(Enum):
        PSN = "psn"
        XBOX = "xbl"
        BATTLENET = "battle"
        ACTIVISION = "uno"

    class Endpoints(Enum):
        # Lists lifetime stats like kd, gun accuracy etc, as well as weekly stats separated by all gamemodes played that week
        profile = "/stats/cod/v1/title/mw/platform/{platform}/{endpointType}/{username}/profile/type/wz"
        # Returns 20 recent matches with everything from team name, team placement to the loadouts everyone used, as well as a summary of your own stats for those matches
        recentMatches = "/crm/cod/v2/title/mw/platform/{platform}/{endpointType}/{username}/matches/wz/start/0/end/0/details"
        # Returns (up to) 20 recent matches, specifying end/start times
        recentMatchesWithDate = "/crm/cod/v2/title/mw/platform/{platform}/{endpointType}/{username}/matches/wz/start/{startTimestamp}/end/{endTimestamp}/details"
        # Returns 1000 recent matches, with only the timestamps, matchIds, mapId, and platform
        matches = "/crm/cod/v2/title/mw/platform/{platform}/{endpointType}/{username}/matches/wz/start/0/end/0"
        # Returns the details of the specific match per player; each players stats from the loadout they used to the kills they got is listed
        matchesWithDate = "/crm/cod/v2/title/mw/platform/{platform}/{endpointType}/{username}/matches/wz/start/{startTimestamp}/end/{endTimestamp}"
        # Returns the details of the specific match per player; each players stats from the loadout they used to the kills they got is listed
        matchDetails = (
            "/crm/cod/v2/title/mw/platform/{platform}/fullMatch/wz/{matchId}/en"
        )

    def __init__(self, sso):
        self.Login(sso)

    def Login(self, sso):
        """
        Login to the Call of Duty API using single sign-on (SSO) authentification
        Method is called on API instance initialization and set the SSO value in headers.

        Parameters
        ----------
        sso: str,
            Activision single sign-on cookie value.
            Inspect browser while loging-in to Activision callofduty and find "act_sso_cookie"

        Returns
        -------
        object
            Authenticated API instance with sso filled-in headers
        """
        auth = Auth(sso)

        if sso is not None:
            self.headers = auth.headers
            self.session = auth.session
            self.loggedIn = True

            return auth

        else:
            raise ValueError("sso value must be provided to communicate to COD API")

    async def _SendGetRequest(self, url):
        """Send a single GET request through httpx.AsyncClient.request"""

        res = await self.session.request("GET", url=url, headers=self.headers)
        if 300 > res.status_code >= 200:
            return res.json()
        else:
            print(f"Error {res.status_code}.\n{res}")

    async def GetProfile(self, platform, username):
        """Get Player Profile"""

        url = Api.baseUrl + Api.Endpoints.profile.value.format(
            platform=platform,
            endpointType="uno" if platform == Api.Platforms.ACTIVISION else "gamer",
            username=urllib.parse.quote(username),
        )
        return await self._SendGetRequest(url)["data"]

    async def GetRecentMatches(self, platform, username):
        """Get username's 20 recent matches.
        Each match entry has username (& teammates) stats, loadouts for this match
        """

        url = Api.baseUrl + Api.Endpoints.recentMatches.value.format(
            platform=platform,
            endpointType="uno" if platform == Api.Platforms.ACTIVISION else "gamer",
            username=urllib.parse.quote(username),
        )
        return await self._SendGetRequest(url)["data"]["matches"]

    async def GetRecentMatchesWithDate(
        self, platform, username, startTimestamp, endTimestamp
    ):
        """Get username's recent matches between two dates.
        Each match entry has username (& teammates) stats, loadouts for this match
        """

        url = Api.baseUrl + Api.Endpoints.recentMatchesWithDate.value.format(
            platform=platform,
            endpointType="uno" if platform == Api.Platforms.ACTIVISION else "gamer",
            username=urllib.parse.quote(username),
            startTimestamp=startTimestamp,
            endTimestamp=endTimestamp,
        )
        return await self._SendGetRequest(url)["data"]["matches"]

        # ["data"]["allPlayers"]

    async def GetMatches(self, platform, username):
        """Get username's last 1000 matches with timestamps, matchIds, mapId, platform (NO stats)"""

        url = Api.baseUrl + Api.Endpoints.matches.value.format(
            platform=platform,
            endpointType="uno" if platform == Api.Platforms.ACTIVISION else "gamer",
            username=urllib.parse.quote(username),
        )
        return await self._SendGetRequest(url)["data"]

    async def GetMatchesWithDate(
        self, platform, username, startTimeStamp, endTimestamp
    ):
        """Get username's matches between two dates, with timestamps, matchIds, mapId, platform (NO stats)"""

        url = Api.baseUrl + Api.Endpoints.matchesWithDate.value.format(
            platform=platform,
            endpointType="uno" if platform == Api.Platforms.ACTIVISION else "gamer",
            username=urllib.parse.quote(username),
            startTimeStamp=startTimeStamp,
            endTimestamp=endTimestamp,
        )
        return await self._SendGetRequest(url)["data"]

    async def GetMatchDetails(self, platform, username, matchId: int):
        """Get ALL players detailed stats for one match, given a specified match id"""

        url = Api.baseUrl + Api.Endpoints.matchDetails.value.format(
            platform=platform,
            endpointType="uno" if platform == Api.Platforms.ACTIVISION else "gamer",
            username=urllib.parse.quote(username),
            matchId=matchId,
        )
        return await self._SendGetRequest(url)["data"]
