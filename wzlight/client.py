import random

import httpx


class Client:

    """
    COD API is not officially supported.

    - httpx library is used to build the wzlight client
    - SSO token value can be found in browser while login-in to callofduty.com. Expiration date is unknown to infinite.
    - Timeout : default timeout (httpx.timeout = 5 sec) have been increased
    - One of rate limit is said to be 200 calls per 30mn-hour, but more restrictions apply under the hood (endpoint variations, IP etc.)
    - Client is set as HTTP/2 but as verified with response.http_version server side protocol is HTTP/1.1
    - Concurrency limit (e.g. for several matches data collection) should be handled at a higher (app) level, through httpx.Limits, asyncio Semaphore or external libraries such as aiometer
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

    timeout = httpx.Timeout(15.0, connect=15.0)
    session = httpx.AsyncClient(http2=True, timeout=timeout)

    def __init__(self, sso=None):
        self.sso = sso
        if self.sso is not None:
            self.sso = sso
            self.headers = Client.headers
            self.headers["Atvi-Auth"] = sso
            self.headers["ACT_SSO_COOKIE"] = sso
            self.headers["atkn"] = sso
            self.headers["cookie"] = Client.cookie.format(
                base_cookie=Client.base_cookie,
                sso=sso,
                xsrf=Client.xsrf,
                deviceId=Client.deviceId,
            )
