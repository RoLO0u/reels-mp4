from aiogram import types, Router, F, html
from aiogram.filters import Command
from aiogram.utils.i18n import gettext as _

from src import const

router = Router()

@router.message(Command("start"), F.chat.type=="private")
async def start(message: types.Message) -> None:
    assert message.from_user

    if message.from_user.id != const.ADMIN_ID:
        text = _("""Hello! This bot is private. \
You are not allowed to use it. Consider deploying it on your own machine. \
<a href='https://github.com/RoLO0u/reels-mp4'>GitHub Link</a> to an open source project. \
Your user ID is <b>{user_id}</b>.""").format(user_id=message.from_user.id)
        await message.answer(text)
        return
    
    await message.answer(
        _("Hi, <b>{name}</b>! Put a link of an instagram reel and I will turn it into an mp4 file for you.")
            .format(name=html.quote(message.from_user.full_name))
    )
    
@router.message(Command("help"), F.chat.type=="private")
async def help(message: types.Message) -> None:

    await message.answer(
        _("This bot is open source and you can use it for yourself by configuring it and deploying it on your machine")
    )
