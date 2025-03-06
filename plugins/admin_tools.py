from datetime import datetime

from core import types, filters
from core.client import KGBot
from utils.utils import user_text


class Help:
    author = 'Koban'
    modules_description = 'Модуль для администратора (бан, кик, мут). ' \
                          'Время указывать необязательно, тогда будет бан навсегда. ' \
                          'Формат времени: 30 | 30s - секунд, 1m - 1 минута, 30h - 30 часов, 10d - 10 дней'
    commands_description = {
        '.ban {айди (юзернейм) пользователя} {время}': 'Забанить пользователя по айди на {время}',
        '.ban [ответ на сообщение] {время}': 'Забанить пользователя по реплаю на {время}',
        '.unban {айди (юзернейм) пользователя}': 'Разбанить пользователя по айди',
        '.unban [ответ на сообщение]': 'Разбанить пользователя по реплаю',
        '.kick {айди (юзернейм) пользователя} {время}': 'Выгнать пользователя по айди на {время}',
        '.kick [ответ на сообщение] {время}': 'Выгнать пользователя по реплаю на {время}',
        '.mute {айди (юзернейм) пользователя} {время}': 'Замутить пользователя по айди на {время}',
        '.mute [ответ на сообщение] {время}': 'Замутить пользователя по реплаю на {время}',
        '.unmute {айди (юзернейм) пользователя}': 'Разбанить пользователя по айди',
        '.unmute [ответ на сообщение]': 'Разбанить пользователя по реплаю',
    }


@KGBot.on_message(filters.me & filters.command('ban'))
async def ban_user_handler(app: KGBot, message: types.Message):
    timer = 0
    if len(message.command) == 3:  # бан со временем по айди
        _, user_id, timer = message.command
    elif len(message.command) == 2 and message.reply_to_message:  # бан со временем по реплаю
        _, timer = message.command
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) == 2:  # бан по айди без времени
        _, user_id = message.command
    elif len(message.command) == 1 and message.reply_to_message:  # бан по реплаю без времени
        user_id = message.reply_to_message.from_user.id
    else:
        return await message.edit_text(user_text('Вы не указали пользователя'))

    seconds_timer = get_time_from_str(timer)
    if seconds_timer is None:
        return await message.edit_text(user_text('Неправильный формат времени'))

    await app.ban_chat_member(message.chat.id, user_id, datetime.now() + int(seconds_timer))
    await message.edit_text(user_text('Пользователь забанен'))


@KGBot.on_message(filters.me & filters.command('unban'))
async def unban_user_handler(app: KGBot, message: types.Message):
    if len(message.command) == 2:  # разбан по айди
        _, user_id = message.command
    elif len(message.command) == 1 and message.reply_to_message:  # разбан по реплаю
        user_id = message.reply_to_message.from_user.id
    else:
        return await message.edit_text(user_text('Вы не указали пользователя'))

    await app.unban_chat_member(message.chat.id, user_id)
    await message.edit_text(user_text('Пользователь разбанен'))


@KGBot.on_message(filters.me & filters.command('kick'))
async def kick_user_handler(app: KGBot, message: types.Message):
    if len(message.command) == 2:  # кик по айди
        _, user_id = message.command
    elif len(message.command) == 1 and message.reply_to_message:  # кик по реплаю
        user_id = message.reply_to_message.from_user.id
    else:
        return await message.edit_text(user_text('Вы не указали пользователя'))

    await app.ban_chat_member(message.chat.id, user_id, datetime.now() + 1)
    await message.edit_text(user_text('Пользователь кикнут'))


@KGBot.on_message(filters.me & filters.command('mute') & filters.reply)
async def mute_user_handler(app: KGBot, message: types.Message):
    timer = 0
    if len(message.command) == 3:  # мут со временем по айди
        _, user_id, timer = message.command
    elif len(message.command) == 2 and message.reply_to_message:  # мут со временем по реплаю
        _, timer = message.command
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) == 2:  # мут по айди без времени
        _, user_id = message.command
    elif len(message.command) == 1 and message.reply_to_message:  # мут по реплаю без времени
        user_id = message.reply_to_message.from_user.id
    else:
        return await message.edit_text(user_text('Вы не указали пользователя'))

    seconds_timer = get_time_from_str(timer)
    if seconds_timer is None:
        return await message.edit_text(user_text('Неправильный формат времени'))

    await app.restrict_chat_member(message.chat.id, user_id, datetime.now() + int(seconds_timer))


def get_time_from_str(time_text: str) -> int:
    """
    Вернет секунды
    :param time_text: время в формате 10, 20s, 1m, 30h, 10d
    """
    if time_text.isdigit():
        return int(time_text)
    if time_text.endswith('s'):
        return int(time_text[:-1])
    if time_text.endswith('m'):
        return int(time_text[:-1]) * 60
    if time_text.endswith('h'):
        return int(time_text[:-1]) * 60 * 60
    if time_text.endswith('d'):
        return int(time_text[:-1]) * 60 * 60 * 24

    return 0
