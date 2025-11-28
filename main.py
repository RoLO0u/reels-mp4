import dotenv
dotenv.load_dotenv(override=True)

import logging

from src import const
from src import bot

def main() -> None:
  logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=const.LOG_LEVEL,
  )
  bot.run(const.BOT_TOKEN)

if __name__ == "__main__":
  main()