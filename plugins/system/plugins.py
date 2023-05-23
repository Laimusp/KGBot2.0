import importlib
import os
from pprint import pprint

from pyrogram import types, filters
from utils.client import KGBot


@KGBot.on_message(filters.command('loadmod', '.'))
async def load_modules_handler(app: KGBot, message: types.Message):
    await message.edit_text('<b><i>Начинается загрузка...</i></b>')
    if not (reply := message.reply_to_message):
        return await message.edit_text('<b><i>Вы не указали <u>модуль</u></i></b>')
    if not (doc := reply.document) or not doc.file_name.endswith('.py'):
        return await message.edit_text('<b><i>Неверный формат модуля</i></b>')

    await reply.download(file_name=f'plugins/{doc.file_name}')
    await message.edit_text(f'<b><i>Модуль <u>{doc.file_name[:-3]}</u> успешно установлен</i></b>')
    await app.modules_restart()


@KGBot.on_message(filters.command('delmod', '.'))
async def delete_modules_handler(app: KGBot, message: types.Message):
    """Отключение модуля"""
    await message.edit_text('<b><i>Начинается удаление...</i></b>')
    if len(message.command) == 1:
        return await message.edit_text('<b><i>Вы не указали <u>модуль</u></i></b>')

    module_name = message.text.split(maxsplit=1)[1].replace(' ', '_')
    if module_name + '.py' not in os.listdir('plugins/'):
        return await message.edit_text('<b><i>Модуль не найден</i></b>')

    module = importlib.import_module(f'plugins.{module_name}')
    handlers = [item for item in module.__dict__.values() if hasattr(item, 'handlers')]
    for handler in handlers:
        _handler, group = handler.handlers[0]
        app.remove_handler(_handler, group)

    await message.edit_text(f'<b><i>Модуль <u>{module_name}</u> успешно удален</i></b>')


@KGBot.on_message(filters.command('fdelmod', '.'))
async def full_delete_modules_handler(_, message: types.Message):
    """Удаление модуля (файла)"""
    await message.edit_text('<b><i>Начинается удаление...</i></b>')
    if len(message.command) == 1:
        return await message.edit_text('<b><i>Вы не указали <u>модуль</u></i></b>')

    module_name = message.text.split(maxsplit=1)[1].replace(' ', '_')
    if module_name + '.py' not in os.listdir('plugins/'):
        return await message.edit_text('<b><i>Модуль не найден</i></b>')

    os.remove(f'plugins/{module_name}.py')
    await message.edit_text(f'<b><i>Модуль <u>{module_name}</u> полностью удален</i></b>')


@KGBot.on_message(filters.command('recovmod', '.'))
async def recovery_modules_handler(app: KGBot, message: types.Message):
    """Отключение модуля"""
    await message.edit_text('<b><i>Начинается удаление...</i></b>')
    if len(message.command) == 1:
        return await message.edit_text('<b><i>Вы не указали <u>модуль</u></i></b>')

    module_name = message.text.split(maxsplit=1)[1].replace(' ', '_')
    if module_name + '.py' not in os.listdir('plugins/'):
        return await message.edit_text('<b><i>Модуль не найден</i></b>')

    module = importlib.import_module(f'plugins.{module_name}')
    importlib.reload(module)
    handlers = [item for item in module.__dict__.values() if hasattr(item, 'handlers')]
    for handler in handlers:
        _handler, group = handler.handlers[0]
        app.add_handler(_handler, group)

    await message.edit_text(f'<b><i>Модуль <u>{module_name}</u> успешно восстановлен</i></b>')
