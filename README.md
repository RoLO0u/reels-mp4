# Reels MP4 Bot

Telegram inline bot that turns any Instagram Reel link into a shareable MP4 video straight inside your chats. Built with [aiogram&nbsp;3](https://github.com/aiogram/aiogram) and [Instaloader](https://github.com/instaloader/instaloader), the bot works entirely through inline queries, so users never have to leave the conversation they are in.

## Features
- Inline-only workflow: type `@your_bot https://www.instagram.com/reel/<shortcode>/` in any chat and get a playable MP4.
- Fallback delivery: if Telegram rejects the inline result (e.g., slow download), the bot DM’s the user with the video.
- Localized responses: English and Ukrainian translations are included via `aiogram.utils.i18n`.
- Minimal surface area: a single `main.py` entry point and a few focused handlers make the code base easy to extend.

## Requirements
- Python 3.11+
- Telegram Bot API token created via [@BotFather](https://t.me/BotFather).
- Instagram reels must be accessible without login; private reels cannot be fetched by Instaloader.

## Quick Start
1. **Clone and enter the project**
	```bash
	git clone https://github.com/RoLO0u/reels-mp4.git
	cd reels-mp4
	```
2. **Create a virtual environment (recommended)**
	```bash
	python3 -m venv .venv
	source .venv/bin/activate
	```
3. **Install dependencies**
	```bash
	pip install -r requirements.txt
	```
4. **Create a `.env` file** (see the configuration section) and run:
	```bash
	python main.py
	```

## Configuration
`python-dotenv` loads environment variables from a local `.env` file. The available options are:

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `BOT_TOKEN` | ✅ | – | Telegram bot token. Without it the bot will refuse to start. |
| `DEBUG` | ❌ | `True` | Enables verbose logging. Set to `False` for quieter logs in production. |
| `SHORTCODE_LENGTH` | ❌ | `11` | Length of the Instagram Reel shortcode; override only if Meta changes their format. |

Example `.env`:

```ini
BOT_TOKEN=1234567890:ABCDEF_bot_token_from_botfather
DEBUG=True
SHORTCODE_LENGTH=11
```

## Running the bot
```bash
python main.py
```
The bot starts polling immediately. Use your private chat to send `/start` or `/help` to confirm it is alive.

## Usage
1. Invite the bot to any chat (or use it in Saved Messages).
2. Type `@<bot_username> <reel_link>` and wait for the inline result to appear.
3. Pick **Send Video** to share the MP4-backed reel. If Telegram times out, the bot sends the video directly to your DM.

## Localization
Translations live under `locales/<language>/LC_MESSAGES/messages.po`. To add a new language:
1. Copy the `locales/en` folder to your desired locale code (e.g., `es`).
2. Translate strings inside `messages.po`.
3. Compile them with `msgfmt locales/<lang>/LC_MESSAGES/messages.po -o locales/<lang>/LC_MESSAGES/messages.mo`.
4. Restart the bot. Users with matching Telegram language codes receive localized replies automatically.

## Troubleshooting
- **Inline result never appears** – Make sure the shortcode inside the reel URL matches `SHORTCODE_LENGTH` (default 11 characters). Non-reel links are ignored silently.
- **`TelegramBadRequest` errors** – Usually caused by Telegram rejecting large payloads. The handler already falls back to sending videos directly, but check your bot’s privacy settings.
- **Rate limits or 429 errors** – Instaloader is scraping Instagram without authentication. Heavy use may trigger throttling; consider adding caching or rotating IPs.

## Contributing
Bug reports, feature ideas, and pull requests are welcome. Please open an issue describing the change you have in mind before submitting large feature work.

## License
Distributed under the MIT License. See `LICENSE` for details.
