import json
import re
from dataclasses import dataclass
from typing import Optional
from src.const import L

# Mimic Instaloader Post object for compatibility
@dataclass
class CffiPost:
    video_url: Optional[str]
    url: str  # thumbnail/display_url
    caption: Optional[str]
    owner_username: str
    video_view_count: int
    likes: int

def download(shortcode: str) -> Optional[CffiPost]:
    import sys
    import os
    from src.const import FROM_SESSION_FILE
    
    print(f"DEBUG: Starting download for {shortcode}")
    print(f"DEBUG: CWD: {os.getcwd()}")
    print(f"DEBUG: FROM_SESSION_FILE: '{FROM_SESSION_FILE}'")
    print(f"DEBUG: File exists? {os.path.exists(FROM_SESSION_FILE) if FROM_SESSION_FILE else 'N/A'}")
    sys.stdout.flush()

    # Use the session from L which is already patched with CurlCffiSession in src/const.py
    # However, Instaloader might have added headers that cause blocks.
    # Let's create a CLEAN session and copy cookies, mirroring custom_download.py success.
    from curl_cffi import requests
    
    # Extract proxies from Instaloader session
    proxies = None
    if L.context._session.proxies:
        print(f"DEBUG: Copying proxies: {L.context._session.proxies}")
        proxies = L.context._session.proxies
    
    # Initialize Session with proxies and impersonation
    # IMPROTANT: Do not manually set User-Agent header, let impersonate handle it to match TLS fingerprint.
    session = requests.Session(
        impersonate="chrome110",
        proxies=proxies # pyright: ignore[reportArgumentType]
    )
    
    # Manually load cookies from session file to avoid Instaloader/Patch issues
    from src.const import FROM_SESSION_FILE
    import pickle
    import os
    
    if FROM_SESSION_FILE and os.path.exists(FROM_SESSION_FILE):
        print(f"DEBUG: Loading session manually from {FROM_SESSION_FILE}")
        try:
            with open(FROM_SESSION_FILE, 'rb') as f:
                session_data = pickle.load(f)
                
            # Session data from Instaloader is typically a RequestsCookieJar or a dict
            cookies_to_add = []
            
            # If it's a CookieJar, iterate it
            if hasattr(session_data, '__iter__'):
                 for c in session_data:
                     cookies_to_add.append(c)
            elif isinstance(session_data, dict):
                 # Some formats might be simple dicts
                 for k, v in session_data.items():
                     session.cookies.set(k, v)
            
            for cookie in cookies_to_add:
                 name = getattr(cookie, 'name', None)
                 value = getattr(cookie, 'value', None)
                 domain = getattr(cookie, 'domain', None)
                 if name and value:
                     if domain:
                         session.cookies.set(name, value, domain=domain)
                     else:
                         session.cookies.set(name, value)
            
            print(f"DEBUG: Manually loaded {len(cookies_to_add)} cookies.")
            
        except Exception as e:
            print(f"Manual session load failed: {e}")
    else:
        print("DEBUG: No session file found or configured.")

    
    # Hardcoded doc_id for Post query (same as Instaloader uses)
    DOC_ID = "8845758582119845"
    
    params = {
        'variables': json.dumps({'shortcode': shortcode}),
        'doc_id': DOC_ID,
        'server_timestamps': 'true'
    }
    
    # Direct GraphQL query using the spoofed session
    resp = session.get(
        "https://www.instagram.com/graphql/query", 
        params=params, 
        timeout=30
    )
    
    if resp.status_code != 200:
        raise Exception(f"Query failed: {resp.status_code} {resp.text[:100]}")
        
    data = resp.json()
    if 'data' not in data:
         raise Exception(f"Invalid JSON response. Data keys: {list(data.keys())}. Content: {resp.text[:500]}")
         
    media = data['data'].get('shortcode_media') or data['data'].get('xdt_shortcode_media')
    if not media:
         print(f"DEBUG: Media not found in JSON. Keys: {list(data['data'].keys())}")
         print("DEBUG: Attempting fallback to HTML scraping...")
         
         # Fallback: Scrape the public HTML page
         # We can reuse the same session to benefit from potential cookies/fingerprint, 
         # but normally public page works without auth too.
         html_resp = session.get(
             f"https://www.instagram.com/reel/{shortcode}/",
             timeout=30
         )
         
         if html_resp.status_code == 200:
             html = html_resp.text
             
             # Regex extraction
             video_url_match = re.search(r'<meta property="og:video" content="([^"]+)"', html)
             image_url_match = re.search(r'<meta property="og:image" content="([^"]+)"', html)
             desc_match = re.search(r'<meta property="og:description" content="([^"]+)"', html)
             
             video_url = video_url_match.group(1) if video_url_match else None
             
             if video_url:
                 print("DEBUG: Fallback successful found video in HTML.")
                 return CffiPost(
                     video_url=video_url,
                     url=image_url_match.group(1) if image_url_match else "",
                     caption=desc_match.group(1) if desc_match else None,
                     owner_username="unknown", # Hard to parse reliably without JSON
                     video_view_count=0,
                     likes=0
                 )
         
         print("DEBUG: Fallback failed.")
         with open("debug_fallback.html", "w") as f:
             f.write(html)
         return None
    
    # Extract Caption safely
    caption = None
    edges = media.get('edge_media_to_caption', {}).get('edges', [])
    if edges:
        caption = edges[0].get('node', {}).get('text')
        
    return CffiPost(
        video_url=media.get('video_url'),
        url=media.get('display_url'),
        caption=caption,
        owner_username=media.get('owner', {}).get('username', 'unknown'),
        video_view_count=media.get('video_view_count', 0),
        likes=media.get('edge_media_preview_like', {}).get('count', 0)
    )
