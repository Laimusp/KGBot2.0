from pyrogram import filters, types
from utils.client import KGBot


class Help:
    author = 'Koban'
    help_commands = ['count']
    modules_description = 'Модуль для получения кол-ва сообщений в чате'
    commands_description = {
        'count': 'Узнать кол-во сообщений в чате'
    }


@KGBot.on_message(filters.me & filters.command('count', KGBot.prefix))
async def count_message_handler(app: KGBot, message: types.Message):
    count = await app.get_chat_history_count(message.chat.id)
    await message.edit_text(f'Кол-во сообщений в чате: {count}')