import httpx
import urllib.parse


class Auth:
    xsrf = "68e8b62e-1d9d-4ce1-b93f-cbe5ff31a041"
    base_cookie = "new_SiteId=cod; ACT_SSO_LOCALE=en_US;country=US;"
    cookie = '{base_cookie}ACT_SSO_COOKIE={sso};XSRF-TOKEN={xsrf};API_CSRF_TOKEN={xsrf};ACT_SSO_EVENT="LOGIN_SUCCESS:1644346543228";ACT_SSO_COOKIE_EXPIRY=1645556143194;comid=cod;ssoDevId=63025d09c69f47dfa2b8d5520b5b73e4;tfa_enrollment_seen=true;gtm.custom.bot.flag=human;'

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

    def __init__(self, sso=None):
        self.sso = sso
        self.session = httpx.AsyncClient()

        if self.sso is not None:
            self.sso = sso
            self.headers = Auth.headers
            self.headers["Atvi-Auth"] = sso
            self.headers["ACT_SSO_COOKIE"] = sso
            self.headers["atkn"] = sso
            self.headers["cookie"] = Auth.cookie.format(
                base_cookie=Auth.base_cookie, sso=sso, xsrf=Auth.xsrf
            )
            self.loggedIn = True
