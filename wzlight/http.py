import urllib.parse

import httpx


class Request:
    """
    Represents a Request object.
    Parameters
    ----------
    method : str
        HTTP method to perform for the reqest.
    endpoint : str, optional
        Endpoint to execute the request on (default is None.)
    baseUrl : str, optional
        Base URL to use for the request (default is https://www.callofduty.com/)
    headers : dict, optional
        Headers to include in the request (default is None.)
    json : dict, optional
        JSON data to include in the body of the request (default is None.)
    """

    defaultBaseUrl = "https://www.callofduty.com/"
    myBaseUrl = "https://my.callofduty.com/"

    accessToken = None
    deviceId = None

    def __init__(self, method, endpoint=None, **kwargs):
        self.method = method
        self.headers = {}
        self.json = kwargs.get("json", {})

        if endpoint is not None:
            baseUrl = kwargs.get("baseUrl", self.defaultBaseUrl)
            self.url = f"{baseUrl}{endpoint}"

        headers = kwargs.get("headers")
        if isinstance(headers, dict):
            self.headers.update(headers)

    def SetHeader(self, key: str, value: str):
        self.headers[key] = value


class HTTP:
    """HTTP client used to communicate with the Call of Duty API."""

    def __init__(self, auth):
        self.auth = auth
        self.session = auth.session

    async def Send(self, req):
        """
        Perform an HTTP request.
        Parameters
        ----------
        req : callofduty.HTTP.Request
            Object representing the HTTP request.
        Returns
        -------
        dict/str
            Response of the HTTP request.
        """

        # // original client : added a timeout httpx object longer than httpx default (5 sec)
        #    because COD API often throws a timeout, early
        timeout = httpx.Timeout(15.0, connect=15.0)

        req.SetHeader("Authorization", f"Bearer {self.auth.AccessToken}")
        req.SetHeader("x_cod_device_id", self.auth.DeviceId)

        async with self.session as client:
            res = await client.request(
                req.method, req.url, headers=req.headers, json=req.json, timeout=timeout
            )

            jsonTypes = [
                "application/json;charset=utf-8",
                "application/json",
            ]
            if res.headers["Content-Type"].lower() in jsonTypes:
                data = res.json()
            else:
                data = res.text

            if isinstance(data, dict):
                status = data.get("status")

                # The API tends to return HTTP 200 even when an error occurs
                if status == "error":
                    raise Exception(res.status_code, data)

            # HTTP 2XX: Success
            if 300 > res.status_code >= 200:
                return data

    async def SearchPlayer(self, platform: str, username: str):
        return await self.Send(
            Request(
                "GET",
                f"api/papi-client/crm/cod/v2/platform/{platform}/username/{urllib.parse.quote(username)}/search",
            )
        )

    # Original client : GetPlayerProfile => GetProfile
    async def GetProfile(self, platform: str, username: str, title: str, mode: str):
        return await self.Send(
            Request(
                "GET",
                f"api/papi-client/stats/cod/v1/title/{title}/platform/{platform}/gamer/{urllib.parse.quote(username)}/profile/type/{mode}",
            )
        )

    # Original client : GetPlayerMatches => GetMatches
    async def GetMatches(
        self,
        platform: str,
        username: str,
        title: str,
        mode: str,
        limit: int,
        startTimestamp: int,
        endTimeStamp: int,
    ):
        return await self.Send(
            Request(
                "GET",
                f"api/papi-client/crm/cod/v2/title/{title}/platform/{platform}/gamer/{urllib.parse.quote(username)}/matches/{mode}/start/{startTimestamp}/end/{endTimeStamp}?limit={limit}",
            )
        )

    # Original client : GetPlayerMatchesDetailed => GetMatchesDetailed
    async def GetMatchesDetailed(
        self,
        platform: str,
        username: str,
        title: str,
        mode: str,
        limit: int,
        startTimestamp: int,
        endTimeStamp: int,
    ):
        return await self.Send(
            Request(
                "GET",
                f"api/papi-client/crm/cod/v2/title/{title}/platform/{platform}/gamer/{urllib.parse.quote(username)}/matches/{mode}/start/{startTimestamp}/end/{endTimeStamp}/details?limit={limit}",
            )
        )

    # Original client : GetFullMatch => GetMatchStats
    async def GetMatchStats(
        self, title: str, platform: str, mode: str, matchId: int, language: str
    ):
        return await self.Send(
            Request(
                "GET",
                f"api/papi-client/crm/cod/v2/title/{title}/platform/{platform}/fullMatch/{mode}/{matchId}/{language}",
            )
        )
