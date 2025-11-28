from urllib.parse import urlparse

from aiogram import types, Router
from aiogram.utils.i18n import gettext as _
from aiogram.types import InlineQueryResultVideo
from aiogram.exceptions import TelegramBadRequest

from src import reels, const

router = Router()

@router.inline_query()
async def inline_download(inline_query: types.InlineQuery) -> None:
  assert inline_query.bot
  
  shortcode = urlparse(inline_query.query).path.rstrip('/').lstrip("/reels/")
  if len(shortcode) != const.SHORTCODE_LENGTH:
    return
  reel = reels.download(shortcode)
  if not reel.video_url or not reel.caption:
    return
  description = _("{caption}\n@{owner_username}\n{video_view_count} views, {likes} likes").format(
    caption=reel.caption,
    owner_username=reel.owner_username,
    video_view_count=reel.video_view_count,
    likes=reel.likes,
  )

  try:
    await inline_query.answer(
      results=[
        InlineQueryResultVideo(
          id=shortcode,
          video_url=reel.video_url,
          mime_type="video/mp4",
          thumbnail_url=reel.url,
          title="Send Video",
          description=description,
        ),
      ],
    )
  except TelegramBadRequest:
    await inline_query.bot.send_video(
      inline_query.from_user.id,
      video=reel.video_url,
      caption=_("The query took too long to process, so here is the video directly.\n\n{description}").format(
        description=description[800:],
      ),
    )