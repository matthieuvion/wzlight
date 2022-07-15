import random

import httpx
import urllib.parse


class Auth:
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

    # COD API is not officially supported, this no no official documentation
    # default httpx.timeout is 5 sec, sometimes not enough for COD API
    # We set a --for now, basic & quite harsh limit in case
    # an app would use client methods (e.g GetMatch) concurrently
    # One of said limit would be be 200 calls per hour

    timeout = httpx.Timeout(15.0, connect=15.0)
    limits = httpx.Limits(max_keepalive_connections=2, max_connections=4)
    session = httpx.AsyncClient(timeout=timeout)

    def __init__(self, sso=None):
        self.sso = sso
        if self.sso is not None:
            self.sso = sso
            self.headers = Auth.headers
            self.headers["Atvi-Auth"] = sso
            self.headers["ACT_SSO_COOKIE"] = sso
            self.headers["atkn"] = sso
            self.headers["cookie"] = Auth.cookie.format(
                base_cookie=Auth.base_cookie,
                sso=sso,
                xsrf=Auth.xsrf,
                deviceId=Auth.deviceId,
            )
