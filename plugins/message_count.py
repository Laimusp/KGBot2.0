from core import filters, types
from core.client import KGBot


class Help:
    author = 'Koban'
    modules_description = 'Модуль для получения кол-ва сообщений в чате'
    commands_description = {
        'count': 'Узнать кол-во сообщений в чате'
    }


@KGBot.on_message(filters.me & filters.command(['count']))
async def count_message_handler(app: KGBot, message: types.Message):
    count = await app.get_chat_history_count(message.chat.id)
    await message.edit_text(f'Кол-во сообщений в чате: {count}')