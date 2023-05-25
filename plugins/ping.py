import logging
import time
from pyrogram import filters, types
from utils.client import KGBot

logger = logging.getLogger(__name__)


@KGBot.on_message(filters.command('ping', '.') & filters.me)
async def ping_handler(_, message: types.Message):
    ping_time = time.time() - time.mktime(message.date.timetuple())
    await message.edit_text(f'<b>Пинг: <code>{ping_time * 100:.2f}</code> мс</b>')