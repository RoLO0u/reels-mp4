import os
import logging

BOT_TOKEN = os.getenv("BOT_TOKEN") or ""
DEBUG = False if os.getenv("DEBUG") == "False" else True
LOG_LEVEL = logging.INFO if DEBUG else logging.WARNING
SHORTCODE_LENGTH = int(os.getenv("SHORTCODE_LENGTH") or "11")