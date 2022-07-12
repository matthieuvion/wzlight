from enum import Enum
import requests

import httpx
import urllib.parse

from auth import Auth


class Api:
    baseurl = "https://my.callofduty.com/api/papi-client"

    class Platforms(Enum):
        PSN = "psn"
        XBOX = "xbl"
        BATTLENET = "battle"
        ACTIVISION = "uno"

    class Endpoints(Enum):
        # Lists lifetime stats like kd, gun accuracy etc, as well as weekly stats separated by all gamemodes played that week
        profile = "/stats/cod/v1/title/mw/platform/{platform}/{endpointType}/{username}profile/type/wz"
        # Returns 20 recent matches with everything from team name, team placement to the loadouts everyone used, as well as a summary of your own stats for those matches
        recentMatches = "/crm/cod/v2/title/mw/platform/{platform}/{endpointType}/{username}/matches/wz/start/0/end/0/details"
        # Returns 1000 recent matches, with only the timestamps, matchIds, mapId, and platform
        matches = "/crm/cod/v2/title/mw/platform/{platform}/{endpointType}/{username}/matches/wz/start/0/end/0"
        # Returns the details of the specific match per player; each players stats from the loadout they used to the kills they got is listed
        matchDetails = (
            "/crm/cod/v2/title/mw/platform/{platform}/fullMatch/wz/{matchId}/en"
        )

    def __init__(self, sso):
        self.Login(sso)

    def Login(self, sso):
        """
        Login to the Call of Duty API using single sign-on (SSO) authentification
        Requires a sso cookie value

        Parameters
        ----------
        sso: str,
            Activision single sign-on cookie value.
            Inspect browser while loging-in to Activision callofduty ("act_sso_cookie")

        Returns
        -------
        object
            Authenticated Call of Duty client (aka instance of Client class with sso value filled in)
        """
        auth = Auth(sso)

        if sso is not None:
            return auth
        else:
            raise ValueError("sso value must be provided to login to COD API")

    async def GetProfile(self, platform, username):
        pass