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

PROXY_CONFIG = load_proxy_config_from_env()
PROXY_URL = PROXY_CONFIG.proxy_url

L = instaloader.Instaloader()

if PROXY_URL:
  L.context._session.proxies.update({ # pyright: ignore[reportPrivateUsage]
    "http": PROXY_URL,
    "https": PROXY_URL,
  })

if USERNAME:
  if FROM_SESSION_FILE:
    L.load_session_from_file(USERNAME, FROM_SESSION_FILE)
  elif PASSWORD:
    L.login(USERNAME, PASSWORD)