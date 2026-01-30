import os
import pickle
import json
import traceback
from curl_cffi import requests
import dotenv
from curl_cffi.requests import ProxySpec

# Load .env
dotenv.load_dotenv(override=True)

SESSION_FILE = os.getenv("FROM_SESSION_FILE") or "session-month_ord"
PROXY = os.getenv("PROXY")
PROXY_AUTH = os.getenv("PROXY_AUTH")
USER_AGENT = os.getenv("USER_AGENT") or "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Shortcode to test (passed as arg or default)
TEST_SHORTCODE = "DUJKl3vgClx" 
# This doc_id is for post info (same as what Instaloader uses)
DOC_ID = "8845758582119845"

def load_session_cookies(filename):
    print(f"Loading session from {filename}...")
    try:
        with open(filename, 'rb') as f:
            data = pickle.load(f)
            # Instaloader pickles a dict-like object or a cookiejar?
            # Usually it's the InstaloaderContext which has _session, 
            # OR it's a direct cookie jar if saved via request.
            # Instaloader saves non-standard pickles.
            # Let's try to extract cookies purely.
            
            # If it was saved by Instaloader, it might be complex.
            # Let's look at raw extraction.
            if isinstance(data, dict):
                return data
            # If it's a list (some formats), convert.
            return data
    except Exception as e:
        print(f"Failed to load session: {e}")
        return None

def main():
    import sys
    shortcode = sys.argv[1] if len(sys.argv) > 1 else TEST_SHORTCODE

    # Setup Proxy
    proxies = ProxySpec()
    if PROXY and PROXY_AUTH:
        user, pwd = PROXY_AUTH.split(":", 1)
        proxy_url = f"http://{user}:{pwd}@{PROXY}"
        proxies["http"] = proxy_url
        proxies["https"] = proxy_url
        print(f"Using Proxy: {PROXY}")

    # Initialize Session
    s = requests.Session(proxies=proxies)
    s.impersonate = "chrome110"
    # s.headers["User-Agent"] = USER_AGENT # Don't override UA when using impersonate!

    # Check IP
    try:
        ip_resp = s.get("https://api.ipify.org?format=json", timeout=10)
        print(f"Current IP: {ip_resp.json()['ip']}")
    except Exception as e:
        print(f"Failed to check IP: {e}")

    # Load Cookies
    # Note: Instaloader's pickle structure is specific. 
    # Usually it's: [cookie_list, ...]
    # We'll try to load it using `instaloader` purely to extract cookies, 
    # then feed them to curl_cffi. This avoids parsing the binary pickle manually.
    import instaloader
    L = instaloader.Instaloader()
    try:
        L.load_session_from_file("month_ord", SESSION_FILE)
        print("Loaded cookies via Instaloader.")
        
        # Transfer cookies to curl_cffi
        # L.context._session.cookies is a RequestsCookieJar
        for cookie in L.context._session.cookies:
            assert cookie.value is not None
            s.cookies.set(cookie.name, cookie.value, domain=cookie.domain)
            
    except Exception as e:
        print(f"Instaloader load failed: {e}. Attempting raw pickle...")
        # Fallback if instaloader is patched or broken
        pass

    print(f"Attempting to fetch data for shortcode: {shortcode}")
    
    # GraphQL Query
    params = {
        'variables': json.dumps({'shortcode': shortcode}),
        'doc_id': DOC_ID,
        'server_timestamps': 'true'
    }
    
    try:
        resp = s.get("https://www.instagram.com/graphql/query", params=params, timeout=30)
        print(f"Status Code: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            # Navigate JSON to find video URL
            try:
                shortcode_media = data['data']['shortcode_media']
                print(f"Type: {shortcode_media.get('__typename')}")
                print(f"Is Video: {shortcode_media.get('is_video')}")
                if shortcode_media.get('is_video'):
                    print(f"Video URL: {shortcode_media.get('video_url')}")
                else:
                    print(f"Image URL: {shortcode_media.get('display_url')}")
                
                print("SUCCESS: Data retrieved via curl_cffi!")
            except KeyError:
                print("Failed to parse expected JSON structure.")
                print(data)
        elif resp.status_code == 401:
            print("FAILURE: 401 Unauthorized (Still blocked).")
            print(resp.text[:500])
        else:
            print(f"Unexpected status: {resp.status_code}")
            print(resp.text[:500])

    except Exception as e:
        traceback.print_exc()

if __name__ == "__main__":
    main()
