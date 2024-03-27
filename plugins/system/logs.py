import os

from pyrogram import types, filters
from utils.client import KGBot


@KGBot.on_message(filters.me & filters.command('logs', KGBot.prefix))
async def get_logs_handler(_, message: types.Message):
    if len(message.command) == 1:
        return await message.edit_text('<b><i>Вы не указали <u>уровень</u> лога</i></b>')
    if (logs_level := message.command[1]) not in ('10', '20', '30', '40', '50'):
        return await message.edit_text('<b><i>Вы указали неверный уровень лога</i></b>')
    if not os.path.exists(f'logs/log{logs_level}.log') or os.stat(f'logs/log{logs_level}.log').st_size == 0:
        return await message.edit_text('<b><i>Лог пуст</i></b>')

    await message.reply_document(document=f'logs/log{logs_level}.log')
    await message.delete()

    os.remove(f'logs/log{logs_level}.log')
