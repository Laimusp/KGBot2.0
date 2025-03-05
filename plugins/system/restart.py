import os
import sys

from core import types, filters
from core.client import KGBot


class Help:
    author = 'Koban'
    modules_description = 'Модуль для перезагрузки бота'
    commands_description = {
        'restart': 'Перезагрузить бота',
        'fullrestart': 'Полная перезагрузка бота'
    }
    

@KGBot.on_message(filters.command('restart') & filters.me)
async def restart_handler(app: KGBot, message: types.Message):
    await message.edit_text('<b><i>Перезагрузка...</i></b>')
    await app.modules_restart()
    await message.edit_text('<b><i>Перезагрузка прошла успешно!</i></b>')


@KGBot.on_message(filters.command('fullrestart') & filters.me)
async def full_restart_handler(app: KGBot, message: types.Message):
    """При рестарте будет передаваться chat_id, message_id"""
    await message.edit_text('<b><i>Полная перезагрузка...</i></b>')
