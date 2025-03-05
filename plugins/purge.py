from core import types, filters
from core.client import KGBot
from utils.utils import user_text


class Help:
    author = 'Koban'
    modules_description = 'Модуль для удаления сообщений по реплаю (от того, которое указали, до нынешнего)'
    commands_description = {
        'purge': 'Удаляет сообщения в чате'
    }


@KGBot.on_message(filters.me & filters.command("purge"))
async def purge_message_handler(app: KGBot, message: types.Message):
    if not message.reply_to_message:
        return await message.edit_text(user_text('Вы не указали откуда надо удалять сообщения'))

    all_message_count = await app.get_chat_history_count(message.chat.id)
    all_messages = []
    for offset in range(0, all_message_count, 10):
        temp_messages = [msg.id async for msg in app.get_chat_history(message.chat.id, offset=offset)]
        if message.reply_to_message.id in temp_messages:
            temp_messages = temp_messages[:temp_messages.index(message.reply_to_message.id) + 1]
            all_messages.extend(temp_messages)
            break

    if not all_messages:
        return await message.edit_text(user_text('Не удалось найти сообщения для удаления'))

    await app.delete_messages(message.chat.id, all_messages)
