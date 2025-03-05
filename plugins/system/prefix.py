from core import filters, types
from core.client import KGBot
from utils.utils import user_text
from utils.env import Env


class Help:
    author = 'Koban'
    modules_description = 'Модуль для изменения префикса'
    commands_description = {
        'prefix': 'Изменить префикс',
        '.now_prefix': 'Показать текущий префикс'
    }

@KGBot.on_message(filters.me & filters.command('prefix'))
async def change_prefix_handler(app: KGBot, message: types.Message):
    message_text_split = message.text.split()
    if len(message_text_split) == 1:
        return await message.edit_text(user_text('Вы не указали префикс'))
    if len(message_text_split) != 2:
        return await message.edit_text(user_text('Префикс не должен содержать пробелов'))

    _, KGBot.prefix = message_text_split
    Env.set('prefix', KGBot.prefix)

    await app.modules_restart()
    await message.edit_text(user_text(f'Вы можете использовать новый префикс <u>{KGBot.prefix}</u>'))


@KGBot.on_message(filters.me & filters.command('now_prefix', ['.', '!', '/']))
async def now_prefix_handler(_, message: types.Message):
    await message.edit_text(user_text(f'Текущий префикс: <u>{KGBot.prefix}</u>'))

