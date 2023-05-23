from pyrogram import types, filters
from utils.client import KGBot


@KGBot.on_message(filters.command('restart', '.') & filters.me)
async def restart_handler(app: KGBot, message: types.Message):
    await message.edit_text('<b><i>Перезагрузка...</i></b>')
    await app.modules_restart()
    await message.edit_text('<b><i>Перезагрузка прошла успешно!</i></b>')
