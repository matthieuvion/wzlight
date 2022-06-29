import random

import httpx

from .client import Client
from .http import HTTP


class Auth:
    """
    Call of Duty authorization flow, using Single Sign-on (SSO)
    """

    registerDeviceUrl = "https://profile.callofduty.com/cod/mapp/registerDevice"

    _accessToken = None
    _deviceId = None

    def __init__(self, sso: str = None):
        self.sso = sso
        self.session = httpx.AsyncClient()

        if self.sso is not None:
            self.session.cookies.set("ACT_SSO_COOKIE", self.sso)

    @property
    def AccessToken(self):
        """
        Returns
        -------
        str
            Access Token which is set during the device registration phase
            of authentication.
        """

        if self._accessToken is None:
            raise Exception("Access Token is null, not authenticated")

        return self._accessToken

    @property
    def DeviceId(self):
        """
        Returns
        -------
        str
            Device ID which is set during the device registration phase
            of authentication.
        """

        if self._deviceId is None:
            raise Exception("DeviceId is null, not authenticated")

        return self._deviceId

    async def RegisterDevice(self):
        """
        Generate and register a Device ID with the Call of Duty API. Set
        the corresponding Access Token if successful.
        """

        self._deviceId = hex(random.getrandbits(128)).lstrip("0x")
        body = {"deviceId": self.DeviceId}

        async with self.session as client:
            res = await client.post(self.registerDeviceUrl, json=body)

            if res.status_code != 200:
                raise Exception(
                    f"Failed to register fake device (HTTP {res.status_code})"
                )

            data = res.json()
            self._accessToken = dict(data)["data"]["authHeader"]


# // Original client : removed authentification with email/password, doable but now need a Captcha Solver...
async def LoginWithSSO(sso: str = None):
    """
    Login to COD API. Requires Single Sign-on (sso) cookie value.
    Inspect/find ACT SSO cookie while login-in Activisition through your platform of choice (bnet, xbox etc.)
    Parameters
    ----------
    sso: str, optional
        Activision single sign-on cookie value.
    Returns
    -------
    object
        Authenticated Call of Duty client.
    """

    auth = Auth(sso)

    if sso is not None:
        await auth.RegisterDevice()

        return Client(HTTP(auth))
