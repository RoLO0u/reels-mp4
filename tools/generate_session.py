import os
import sys
import instaloader
import dotenv

# Add root dir to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load .env
dotenv.load_dotenv(override=True)

from src.proxy import load_proxy_config_from_env

def generate_session():
    username = os.getenv("INSTA_USERNAME")
    password = os.getenv("PASSWORD")
    
    if not username or not password:
        print("Error: INSTA_USERNAME and PASSWORD must be set in .env")
        return

    print(f"Logging in as {username}...")
    
    # Configure Proxy
    config = load_proxy_config_from_env()
    L = instaloader.Instaloader()
    
    # Use proxy if available (optional for local generation, but safer matches server usage)
    if config.requests_proxies:
        print(f"Using proxy: {config.proxy_url.split('@')[-1]}") # minimal log
        L.context._session.proxies.update(config.requests_proxies)

    try:
        L.login(username, password)
        print("Login Successful!")
    except instaloader.TwoFactorAuthRequiredException:
        code = input("2FA Code Required. Enter SMS/App code: ")
        L.two_factor_login(code)
        print("2FA Login Successful!")
    except Exception as e:
        print(f"Login Failed: {e}")
        return

    filename = f"session-{username}"
    L.save_session_to_file(filename=filename)
    print(f"Session saved to {filename}")

if __name__ == "__main__":
    generate_session()
