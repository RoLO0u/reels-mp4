import os
import logging

import instaloader

BOT_TOKEN = os.getenv("BOT_TOKEN") or ""
DEBUG = False if os.getenv("DEBUG") == "False" else True
LOG_LEVEL = logging.INFO if DEBUG else logging.WARNING
SHORTCODE_LENGTH = 11
USERNAME = os.getenv("USERNAME") or ""
PASSWORD = os.getenv("PASSWORD") or ""
FROM_SESSION_FILE = os.getenv("FROM_SESSION_FILE") or ""
L = instaloader.Instaloader()
if FROM_SESSION_FILE:
  L.load_session_from_file(USERNAME, FROM_SESSION_FILE)
else:
  L.login(USERNAME, PASSWORD)