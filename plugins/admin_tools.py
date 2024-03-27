from pyrogram import types, filters
from utils.client import KGBot


class Help:
    author = 'Koban'
    help_commands = ['e']
    modules_description = 'Модуль для администратора (бан, кик, мут). ' \
                          'Время указывать необязательно, тогда будет бан навсегда. ' \
                          'Формат времени: 1m - 1 минута, 30h - 30 часов, 10d - 10 дней'
    commands_description = {
        '.ban {айди (юзернейм) пользователя} {время}': 'Забанить пользователя по айди на {время}',
        '.ban [ответ на сообщение] {время}': 'Забанить пользователя по реплаю на {время}'
    }


@KGBot.on_message(filters.me & filters.command('ban', KGBot.prefix))
async def ban_user_handler(_, message: types.Message):
    timer = 0
    if len(message.command) == 3:  # бан со временем по айди
        _, user_id, timer = message.command
    elif len(message.command) == 2 and message.reply_to_message:  # бан со временем по реплаю
        _, timer = message
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) == 2:  # бан по айди без времени
        _, user_id = message.command
    elif len(message.command) == 1 and message.reply_to_message:  # бан по реплаю без времени
        user_id = message.reply_to_message.from_user.id
    else:
        return await message.edit_text('<b><i>Вы не указали пользователя</i></b>')

    seconds_timer = get_time_from_str(timer)
    if seconds_timer is None:
        return await message.edit_text('<b><i>Неправильный формат времени</i></b>')


def get_time_from_str(time_text: str) -> int:
    """Вернет секунды"""
    time_info = {'m': 60, 'h': 60 * 60, 'd': 60 * 60 * 24}
    if len(time_info) < 2:
        return None

    *nums, char = time_text
    if all([item.isdigit() for item in nums]) and char in time_info.keys():
        return int(''.join(nums)) * time_info[char]

    return None