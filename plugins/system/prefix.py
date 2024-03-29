from pyrogram import types, filters
from utils.client import KGBot
from utils.utils import user_text


@KGBot.on_message(filters.me & filters.command('prefix', KGBot.prefix))
async def change_prefix_handler(app: KGBot, message: types.Message):
    message_text_split = message.text.split()
    if len(message_text_split) == 1:
        return await message.edit_text(user_text('Вы не указали префикс'))
    if len(message_text_split) != 2:
        return await message.edit_text(user_text('Префикс не должен содержать пробелов'))

    _, KGBot.prefix = message_text_split
    await app.modules_restart()

    await message.edit_text(user_text(f'Вы можете использовать новый префикс <u>{KGBot.prefix}</u>'))