from datetime import datetime, timedelta

from core import types, filters
from core.client import KGBot
from utils.database import Database
from utils.utils import user_text
from utils.decorators import database_decorator


class Help:
    author = 'Koban'
    modules_description = 'AFK-режим'
    commands_description = {
        'afk': 'Включить AFK-режим',
        'afk [текст]': 'Включить AFK-режим с заданным текстом',
        'unafk': 'Выключить AFK-режим',
    }


afk_info = {
    'now_afk': False,
    'afk_text': 'На данный момент AFK',
    'start_afk_time': datetime.now(),
}

afk_stats = {}
# {user_id: last_answer_time}

now_afk_filters = filters.create(lambda _, __, ___: afk_info['now_afk'])


@KGBot.on_message(filters.me & filters.command("afk"))
@database_decorator
async def start_afk_handler(_, message: types.Message, db: Database):
    if afk_info['now_afk']:
        return await message.edit_text(user_text('Вы уже AFK'))

    if len(message_info := message.text.split(maxsplit=1)) > 1:
        afk_info['afk_text'] = message_info[1]
        db.set('afk_text', message_info[1])
    elif 'afk_text' in db.keys():
        afk_info['afk_text'] = db['afk_text']

    afk_info['now_afk'] = True
    afk_info['start_afk_time'] = datetime.now()

    await message.edit_text(user_text('AFK-режим активирован'))


@KGBot.on_message(filters.me & filters.command("unafk"))
async def stop_afk_handler(_, message: types.Message):
    if not afk_info['now_afk']:
        return await message.edit_text(user_text('Вы не AFK'))

    afk_info['now_afk'] = False

    await message.edit_text(user_text('AFK-режим деактивирован'))


@KGBot.on_message(~filters.me & filters.private & now_afk_filters)
async def afk_handler(_, message: types.Message):
    last_message_time = afk_stats.get(message.from_user.id, datetime(1900, 1, 1))
    if datetime.now() - last_message_time > timedelta(minutes=10):
        await message.reply(get_afk_message())
        afk_stats[message.from_user.id] = datetime.now()


def get_afk_message():
    now_afk_time = datetime.now() - afk_info['start_afk_time']
    return user_text(f'AFK уже {now_afk_time}\n\n' + afk_info["afk_text"])