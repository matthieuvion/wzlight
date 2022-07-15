from enum import Enum
import requests

import httpx
import urllib.parse

from .auth import Auth


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
        match = "/crm/cod/v2/title/mw/platform/{platform}/fullMatch/wz/{matchId}/en"

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

        auth = Auth(sso)

        if sso is not None:
            self.headers = auth.headers
            self.session = auth.session
            self.loggedIn = True

            return auth

        else:
            raise ValueError("sso value must be provided to communicate with COD API")

    async def _SendRequest(self, url):
        """Send a single GET request with httpx.AsyncClient.request"""

        response = await self.session.request("GET", url=url, headers=self.headers)
        if 300 > response.status_code >= 200:
            data = response.json()
            return data
        else:
            print(f"Error {response.status_code}.\n{response}")

    async def GetProfile(self, platform, username):
        """Get Player Profile, platform must matches username (e.g acti username =/ bnet)"""

        url = Api.baseUrl + Api.Endpoints.profile.value.format(
            platform=platform,
            endpointType="uno" if platform == Api.Platforms.ACTIVISION else "gamer",
            username=urllib.parse.quote(username),
        )
        data = await self._SendRequest(url)
        return data["data"]

    async def GetRecentMatches(self, platform, username):
        """Get username's 20 recent matches.
        Each match entry has username (& teammates) stats, loadouts for this match
        """

        url = Api.baseUrl + Api.Endpoints.recentMatches.value.format(
            platform=platform,
            endpointType="uno" if platform == Api.Platforms.ACTIVISION else "gamer",
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

        url = Api.baseUrl + Api.Endpoints.recentMatchesWithDate.value.format(
            platform=platform,
            endpointType="uno" if platform == Api.Platforms.ACTIVISION else "gamer",
            username=urllib.parse.quote(username),
            startTimestamp=startTimestamp,
            endTimestamp=endTimestamp,
        )
        data = await self._SendRequest(url)
        return data["data"]["matches"]

    async def GetMatches(self, platform, username):
        """Get username's last 1000 matches with timestamp, matchId, type, mapId, platform (NO stats)"""

        url = Api.baseUrl + Api.Endpoints.matches.value.format(
            platform=platform,
            endpointType="uno" if platform == Api.Platforms.ACTIVISION else "gamer",
            username=urllib.parse.quote(username),
        )
        data = await self._SendRequest(url)
        return data["data"]

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
        data = await self._SendRequest(url)
        return data["data"]["matches"]

    async def GetMatch(self, platform, matchId: int):
        """Get ALL players detailed stats for one match, given a specified match id"""

        url = Api.baseUrl + Api.Endpoints.match.value.format(
            platform=platform,
            endpointType="uno" if platform == Api.Platforms.ACTIVISION else "gamer",
            matchId=matchId,
        )
        data = await self._SendRequest(url)
        return data["data"]["allPlayers"]
