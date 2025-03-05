import os

from core import types, filters
from core.client import KGBot
from utils.utils import user_text


class Help:
    author = 'Koban'
    modules_description = 'Модуль для получения логов'
    commands_description = {
        'logs': 'Получить лог',
        'logs_type [show | file]': 'Изменить тип лога'
    }


@KGBot.on_message(filters.me & filters.command('logs'))
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


@KGBot.on_message(filters.me & filters.command('logs_type'))
async def set_logs_type_handler(_, message: types.Message):
    if len(message.command) == 1:
        return await message.edit_text(user_text('Вы не указали тип лога: show или file'))

    if (logs_type := message.command[1].lower()) not in ('show', 'file'):
        return await message.edit_text(user_text('Вы указали неверный тип лога: show или file'))

    KGBot.logs_type = logs_type

    await message.edit_text(user_text('Новый тип лога успешно установлен'))