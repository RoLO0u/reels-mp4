import os
import logging

import instaloader

from src.proxy import load_proxy_config_from_env

BOT_TOKEN = os.getenv("BOT_TOKEN") or ""
DEBUG = False if os.getenv("DEBUG") == "False" else True
LOG_LEVEL = logging.INFO if DEBUG else logging.WARNING
SHORTCODE_LENGTH = 11
USERNAME = os.getenv("INSTA_USERNAME") or ""
PASSWORD = os.getenv("PASSWORD") or ""
FROM_SESSION_FILE = os.getenv("FROM_SESSION_FILE") or ""
USER_AGENT = os.getenv("USER_AGENT") or "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

PROXY_CONFIG = load_proxy_config_from_env()
PROXY_URL = PROXY_CONFIG.proxy_url

from curl_cffi import requests as cffi_requests
import instaloader.instaloadercontext

# Setup CurlCffi Session Wrapper
class CurlCffiSession(cffi_requests.Session):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Default to chrome impersonation
        self.impersonate = "chrome110"
        # cookie jar compatibility layer might be needed if curl_cffi uses simple dicts
        # requests.utils.dict_from_cookiejar iterates over the jar.
        # curl_cffi tokens might differ.

    def request(self, method, url, *args, **kwargs):
        # Ensure impersonate is passed if not present
        if "impersonate" not in kwargs:
            kwargs["impersonate"] = self.impersonate
        
        # DEBUG: Print request details to verify impersonation
        # print(f"DEBUG: CurlCffi Request: {method} {url} | Impersonate: {kwargs.get('impersonate')}")
        
        resp = super().request(method, url, *args, **kwargs)
        # Patch missing attributes for compatibility with requests
        if not hasattr(resp, "is_redirect"):
             resp.is_redirect = resp.status_code in (301, 302, 303, 307, 308) # pyright: ignore[reportAttributeAccessIssue]
        return resp

# MONKEY PATCH: Instaloader expects standard RequestsCookieJar behavior.
# curl_cffi session.cookies is a CurlCffiCookieJar, but let's verify if iterating acts like Cookie objects.
# The error 'str object has no attribute name' implies that iterating over the jar yields strings (keys?) instead of objects with .name/.value attributes.
# We need to bridge this.
import requests.cookies

# We will patch 'requests.utils.dict_from_cookiejar' to handle curl_cffi jars gracefully if needed, 
# OR ensure our session uses a standard RequestsCookieJar.
# Easiest way: Swizzle the cookiejar to be standard requests one if possible, or patch the utility.

def safe_dict_from_cookiejar(cj):
    if hasattr(cj, 'get_dict'): 
        return cj.get_dict()
    # Fallback to standard request utils
    try:
        return {c.name: c.value for c in cj}
    except AttributeError:
        # If iteration yields strings (keys), it's likely a dict-like object
        return dict(cj)

# Patch requests.utils because Instaloader calls it directly
cffi_requests.utils.dict_from_cookiejar = safe_dict_from_cookiejar # pyright: ignore[reportAttributeAccessIssue]
import requests.utils
requests.utils.dict_from_cookiejar = safe_dict_from_cookiejar

# MONKEY PATCH: Force Instaloader to use our Session class everywhere
instaloader.instaloadercontext.requests.Session = CurlCffiSession # pyright: ignore[reportPrivateImportUsage]

L = instaloader.Instaloader(user_agent=USER_AGENT)

if USERNAME:
  if FROM_SESSION_FILE:
    # Load session (which will now use CurlCffiSession internally)
    L.load_session_from_file(USERNAME, FROM_SESSION_FILE)
  elif PASSWORD:
    L.login(USERNAME, PASSWORD)

if PROXY_URL:
  L.context._session.proxies.update({ # pyright: ignore[reportPrivateUsage]
    "http": PROXY_URL,
    "https": PROXY_URL,
  })