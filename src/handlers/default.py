from aiogram import types, Router, F, html
from aiogram.filters import Command
from aiogram.utils.i18n import gettext as _

router = Router()

@router.message(Command("start"), F.chat.type=="private")
async def start(message: types.Message) -> None:
    assert message.from_user and message.bot

    bot_info = await message.bot.get_me()

    await message.answer(
        _("Hi, <b>{name}</b>! This bot operates by inline queries. To use it, \
type @{bot_username} followed by the link to the reel in any chat. \
Have a little patience as it processes the request. Enjoy!\n\
Check out the source code on GitHub: \
<a href='https://github.com/RoLO0u/reels-mp4'>GitHub Repository</a>")
            .format(name=html.quote(message.from_user.full_name), bot_username=bot_info.username)
    )
    
@router.message(Command("help"), F.chat.type=="private")
async def help(message: types.Message) -> None:

    await message.answer(
        _("This bot is open source and you can deploy it for yourself by configuring it and deploying it on your machine")
    )
