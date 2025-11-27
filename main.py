import logging
import dotenv

from src import const
from src import bot

def main() -> None:
  dotenv.load_dotenv()
  logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=const.DEBUG,
  )
  bot.run(const.BOT_TOKEN)

if __name__ == "__main__":
  main()