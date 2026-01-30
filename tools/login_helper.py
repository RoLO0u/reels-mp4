import os
import time
import sys
import instaloader
import dotenv

# Load .env
dotenv.load_dotenv(override=True)

# Patch Context to allow setting items
from instaloader.instaloadercontext import InstaloaderContext
def patch_login(ctx, user, passwd):
    ctx._session.headers.update({'Referer': 'https://www.instagram.com/'})
    ctx.login(user, passwd)

def login_loop():
    username = os.getenv("INSTA_USERNAME")
    password = os.getenv("PASSWORD")
    proxy = os.getenv("PROXY")
    proxy_auth = os.getenv("PROXY_AUTH")
    user_agent = os.getenv("USER_AGENT")

    if not username or not password:
        print("Missing credentials.")
        return

    print(f"Starting Login Loop for {username}...")
    
    # Setup Instaloader
    L = instaloader.Instaloader(user_agent=user_agent)
    
    # Setup Proxy
    if proxy and proxy_auth:
        user, pwd = proxy_auth.split(":", 1)
        proxy_url = f"http://{user}:{pwd}@{proxy}"
        print(f"Using Proxy: {proxy}")
        L.context._session.proxies.update({"http": proxy_url, "https": proxy_url})

    max_retries = 5
    for i in range(max_retries):
        print(f"\n[Attempt {i+1}/{max_retries}] Logging in...")
        try:
            L.login(username, password)
            print("SUCCESS: Login completed!")
            filename = f"session-{username}"
            L.save_session_to_file(filename=filename)
            print(f"Session saved to {filename}")
            return
        except instaloader.LoginException as e:
            msg = str(e)
            if "Checkpoint required" in msg:
                print("\n" + "="*60)
                print("ACTION REQUIRED: CHECKPOINT TRIGGERED")
                print("Go to this URL in your browser (where you are logged in):")
                # Extract URL if possible, or usually it's in the exception string
                # Regex or just print the exception line cleanly
                import re
                urls = re.findall(r'https://www.instagram.com/challenge/[a-zA-Z0-9_/-]+', msg)
                if urls:
                    print(f"\n{urls[0]}\n")
                else:
                    print(f"\n{msg}\n")
                print("Once you approve 'This was me', wait...")
                print("Retrying in 30 seconds...")
                print("="*60 + "\n")
                time.sleep(30) # Wait for user
            else:
                print(f"Login failed: {e}")
                break
        except Exception as e:
            print(f"Unexpected error: {e}")
            break

if __name__ == "__main__":
    login_loop()
