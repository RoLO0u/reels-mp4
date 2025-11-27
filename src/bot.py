from typing import Tuple

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware

from src import handlers

def create(token: str) -> Tuple[Bot, Dispatcher]:
	bot = Bot(
		token=token,
		default=DefaultBotProperties(parse_mode=ParseMode.HTML),
	)
	i18n = I18n(path="locales", default_locale="en", domain="messages")
	i18n_middleware = SimpleI18nMiddleware(i18n)
	dispatcher = Dispatcher(name="main")
	dispatcher.include_routers(*handlers.routers)
	dispatcher.update.middleware(i18n_middleware)

	return bot, dispatcher

async def polling(dispatcher: Dispatcher, bot: Bot) -> None:
	try:
		await dispatcher.start_polling(
			bot, 
			allowed_updates=dispatcher.resolve_used_update_types())
	finally:
		await bot.session.close()

def run(token: str) -> None:
	bot, dispatcher = create(token)

	asyncio.run(polling(dispatcher, bot))