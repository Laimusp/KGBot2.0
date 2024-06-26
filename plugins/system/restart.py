import os
import sys

from pyrogram import types, filters
from utils.client import KGBot


@KGBot.on_message(filters.command('restart', KGBot.prefix) & filters.me)
async def restart_handler(app: KGBot, message: types.Message):
    await message.edit_text('<b><i>Перезагрузка...</i></b>')
    await app.modules_restart()
    await message.edit_text('<b><i>Перезагрузка прошла успешно!</i></b>')


@KGBot.on_message(filters.command('fullrestart', KGBot.prefix) & filters.me)
async def full_restart_handler(app: KGBot, message: types.Message):
    """При рестарте будет передаваться chat_id, message_id"""
    await message.edit_text('<b><i>Полная перезагрузка...</i></b>')
