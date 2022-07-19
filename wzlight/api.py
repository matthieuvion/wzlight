import random
from functools import wraps
import urllib.parse

from .enums import Endpoints, Platforms


class Api:

    """
    COD API is not officially supported.

    - SSO token can be found in browser while login-in to callofduty.com. Expiration date is unknown to infinite.
    - One of rate limit is said to be 200 calls per 30mn-hour, but more restrictions apply under the hood (endpoint variations, IP etc.)
    - Initially the wrapper had an httpx.AsyncClient() defined in a separate Cls but letting the users use their own context
      manager (with httpx.AsyncClient() as...) at app-level offers way more flexibility and control (also prevent async closed loop errors)
    - Notably, for everything concurrency/throttlers etc.. look at httpx.Limits, asyncio Semaphore or external libraries such as aiometer
    """

    deviceId = hex(random.getrandbits(128)).lstrip(
        "0x"
    )  #  any fake deviceId would works

    xsrf = "mtv2tU5lFIz9ic_V7a4mzmwCZZTe3iNGTkwmkjovIjJdO_VFJvcRHVFJKsQlVFUA"
    base_cookie = "new_SiteId=cod; ACT_SSO_LOCALE=en_US;country=US;"
    cookie = '{base_cookie}ACT_SSO_COOKIE={sso};XSRF-TOKEN={xsrf};API_CSRF_TOKEN={xsrf};ACT_SSO_EVENT="LOGIN_SUCCESS:1644346543228";ACT_SSO_COOKIE_EXPIRY=1645556143194;comid=cod;ssoDevId={deviceId};tfa_enrollment_seen=true;gtm.custom.bot.flag=human;'

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        "Content-Type": "application/json",
        "X-XSRF-TOKEN": xsrf,
        "X-CSRF-TOKEN": xsrf,
        "Atvi-Auth": None,
        "ACT_SSO_COOKIE": None,
        "atkn": None,
        "cookie": None,
    }
    baseUrl = "https://my.callofduty.com/api/papi-client"

    def __init__(self, sso=None):
        self.sso = sso
        self._login()

    def _login(self):
        """
        Login to the Call of Duty API using single sign-on (SSO) authentification
        Method is called on API instance initialization and set the SSO value in client headers.

        Parameters
        ----------
        sso: str,
            Activision single sign-on cookie value ("MjYy[...]xNzAw" alike).
            Inspect browser while loging-in to Activision callofduty and find "act_sso_cookie"
        """

        if self.sso is not None:
            self.headers = Api.headers
            self.headers["Atvi-Auth"] = self.sso
            self.headers["ACT_SSO_COOKIE"] = self.sso
            self.headers["atkn"] = self.sso
            self.headers["cookie"] = Api.cookie.format(
                base_cookie=Api.base_cookie,
                sso=self.sso,
                xsrf=Api.xsrf,
                deviceId=Api.deviceId,
            )
            self.loggedIn = True

        else:
            raise ValueError("SSO token must be provided to communicate with COD API")

    def _setPlatform(self, platform):
        if platform not in [platform.value for platform in Platforms]:
            raise ValueError(
                "platform arg must be either:\nbattle, xbl, psn, acti, uno"
            )
        else:
            platform = (
                "uno" if platform in [Platforms.ACTIVISION, Platforms.UNO] else platform
            )
        return platform

    def _setEndpointType(self, platform):
        endpointType = "id" if platform == Platforms.UNO else "gamer"
        return endpointType

    async def _fetch(self, httpxClient, url):
        """Send a single GET request with httpx.AsyncClient.request"""

        if not self.loggedIn:
            return "You must initialize the Api with an SSO token"

        else:
            response = await httpxClient.get(url, headers=self.headers)
            if 300 > response.status_code >= 200:
                data = response.json()
                return data
            else:
                print(f"Error {response.status_code}.\n{response}")

    async def GetProfile(self, httpxClient, platform, username):
        """Get Player Profile, platform must matches username (e.g acti username =/ bnet)"""

        url = Api.baseUrl + Endpoints.profile.value.format(
            platform=self._setPlatform(platform),
            endpointType=self._setEndpointType(platform),
            username=urllib.parse.quote(username),
        )
        data = await self._fetch(httpxClient, url)
        return data["data"]

    async def GetRecentMatches(self, httpxClient, platform, username):
        """Get username's 20 recent matches.
        Each match entry has username (& teammates) stats, loadouts for this match
        """

        url = Api.baseUrl + Endpoints.recentMatches.value.format(
            platform=self._setPlatform(platform),
            endpointType=self._setEndpointType(platform),
            username=urllib.parse.quote(username),
        )
        data = await self._fetch(httpxClient, url)
        return data["data"]["matches"]

    async def GetRecentMatchesWithDate(
        self, httpxClient, platform, username, endTimestamp
    ):
        """Get username's recent matches between two dates (startTimestamp is always 0, though)
        Each match entry has username (& teammates) stats, loadouts for this match
        """

        url = Api.baseUrl + Endpoints.recentMatchesWithDate.value.format(
            platform=self._setPlatform(platform),
            endpointType=self._setEndpointType(platform),
            username=urllib.parse.quote(username),
            startTimestamp=0,
            endTimestamp=endTimestamp,
        )
        data = await self._fetch(httpxClient, url)
        return data["data"]["matches"]

    async def GetMatches(self, httpxClient, platform, username):
        """Get username's last 1000 matches with timestamp, matchId, type, mapId, platform (NO stats)
        TODO : check is StartTimeStamp is allowed or if same behavior as RecentMatchesWithDate
        """

        url = Api.baseUrl + Endpoints.matches.value.format(
            platform=self._setPlatform(platform),
            endpointType=self._setEndpointType(platform),
            username=urllib.parse.quote(username),
        )
        data = await self._fetch(httpxClient, url)
        return data["data"]

    async def GetMatchesWithDate(
        self, httpxClient, platform, username, startTimeStamp, endTimestamp
    ):
        """Get username's matches between two dates, with timestamps, matchIds, mapId, platform (NO stats)"""

        url = Api.baseUrl + Endpoints.matchesWithDate.value.format(
            platform=self._setPlatform(platform),
            endpointType=self._setEndpointType(platform),
            username=urllib.parse.quote(username),
            startTimeStamp=startTimeStamp,
            endTimestamp=endTimestamp,
        )
        data = await self._fetch(httpxClient, url)
        return data["data"]["matches"]

    async def GetMatch(self, httpxClient, platform, matchId: int):
        """Get ALL players detailed stats for one match, given a specified match id"""

        url = Api.baseUrl + Endpoints.match.value.format(
            platform=self._setPlatform(platform),
            matchId=matchId,
        )
        data = await self._fetch(httpxClient, url)
        return data["data"]["allPlayers"]
