from aiogram import types, Router, F, html
from aiogram.filters import Command
from aiogram.utils.i18n import gettext as _

router = Router()

@router.message(Command("start"), F.chat.type=="private")
async def start(message: types.Message) -> None:
    assert message.from_user
    print(message)
    
    await message.answer(_("Hi, {name}!").format(name=html.quote(message.from_user.full_name)))
    
@router.message(Command("help"), F.chat.type=="private")
async def help(message: types.Message) -> None:

    await message.answer(
        _("This bot is open source and you can use it for yourself by configuring it and deploying it on your machine")
    )
