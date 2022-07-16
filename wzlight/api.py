from functools import wraps
import urllib.parse
from inspect import signature


from .client import Client
from .enums import Endpoints, Platforms


class Api:

    baseUrl = "https://my.callofduty.com/api/papi-client"

    def __init__(self, sso):
        self._Login(sso)

    def _Login(self, sso):
        """
        Login to the Call of Duty API using single sign-on (SSO) authentification
        Method is called on API instance initialization and set the SSO value in client headers.

        Parameters
        ----------
        sso: str,
            Activision single sign-on cookie value.
            Inspect browser while loging-in to Activision callofduty and find "act_sso_cookie"
        """

        auth = Client(sso)

        if sso is not None:
            self.headers = auth.headers
            self.session = auth.session
            self.loggedIn = True

            return auth

        else:
            raise ValueError("sso value must be provided to communicate with COD API")

    async def _SendRequest(self, url):
        """Send a single GET request with httpx.AsyncClient.request"""

        if not self.loggedIn:
            return "You must initialize the Api with an SSO token"

        response = await self.session.request("GET", url=url, headers=self.headers)
        if 300 > response.status_code >= 200:
            print(response.http_version)
            data = response.json()
            return data
        else:
            print(f"Error {response.status_code}.\n{response}")

    async def GetProfile(self, platform, username):
        """Get Player Profile, platform must matches username (e.g acti username =/ bnet)"""

        url = Api.baseUrl + Endpoints.profile.value.format(
            platform=platform,
            endpointType="uno" if platform == Platforms.ACTIVISION else "gamer",
            username=urllib.parse.quote(username),
        )
        data = await self._SendRequest(url)
        return data["data"]

    async def GetRecentMatches(self, platform, username):
        """Get username's 20 recent matches.
        Each match entry has username (& teammates) stats, loadouts for this match
        """

        url = Api.baseUrl + Endpoints.recentMatches.value.format(
            platform=platform,
            endpointType="uno" if platform == Platforms.ACTIVISION else "gamer",
            username=urllib.parse.quote(username),
        )
        data = await self._SendRequest(url)
        return data["data"]["matches"]

    async def GetRecentMatchesWithDate(
        self, platform, username, startTimestamp, endTimestamp
    ):
        """Get username's recent matches between two dates.
        Each match entry has username (& teammates) stats, loadouts for this match
        """

        url = Api.baseUrl + Endpoints.recentMatchesWithDate.value.format(
            platform=platform,
            endpointType="uno" if platform == Platforms.ACTIVISION else "gamer",
            username=urllib.parse.quote(username),
            startTimestamp=startTimestamp,
            endTimestamp=endTimestamp,
        )
        data = await self._SendRequest(url)
        return data["data"]["matches"]

    async def GetMatches(self, platform, username):
        """Get username's last 1000 matches with timestamp, matchId, type, mapId, platform (NO stats)"""

        url = Api.baseUrl + Endpoints.matches.value.format(
            platform=platform,
            endpointType="uno" if platform == Platforms.ACTIVISION else "gamer",
            username=urllib.parse.quote(username),
        )
        data = await self._SendRequest(url)
        return data["data"]

    async def GetMatchesWithDate(
        self, platform, username, startTimeStamp, endTimestamp
    ):
        """Get username's matches between two dates, with timestamps, matchIds, mapId, platform (NO stats)"""

        url = Api.baseUrl + Endpoints.matchesWithDate.value.format(
            platform=platform,
            endpointType="uno" if platform == Platforms.ACTIVISION else "gamer",
            username=urllib.parse.quote(username),
            startTimeStamp=startTimeStamp,
            endTimestamp=endTimestamp,
        )
        data = await self._SendRequest(url)
        return data["data"]["matches"]

    async def GetMatch(self, platform, matchId: int):
        """Get ALL players detailed stats for one match, given a specified match id"""

        url = Api.baseUrl + Endpoints.match.value.format(
            platform=platform,
            endpointType="uno" if platform == Platforms.ACTIVISION else "gamer",
            matchId=matchId,
        )
        data = await self._SendRequest(url)
        return data["data"]["allPlayers"]
