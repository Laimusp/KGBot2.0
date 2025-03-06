from core import types, filters
from core.client import KGBot
from utils.utils import user_text
from utils.decorators import database_decorator
from utils.database import Database
from openai import AsyncOpenAI


ANSWER_TEXT_FORMAT = '<b>Запрос:</b>\n<pre>{message}</pre>\n\n<b>Ответ:</b>\n<pre>{answer}</pre>'


@KGBot.on_message(filters.me & filters.command("ai"))
@database_decorator
async def get_ai_content_handler(_, message: types.Message, database: Database):
    secret_key = await database.get('secret_key', None)
    if not secret_key:
        return await message.edit_text(user_text("Не установлен секретный ключ"))
    
    if len(message.command) < 2:
        return await message.edit_text(user_text("Не указано сообщение"))
    
    await message.edit_text(user_text("Получение ответа..."))

    for count in range(3):
        client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=secret_key,
        )

        message_text = message.text.split(maxsplit=1)[1].strip()
        response = await client.chat.completions.create(
            model="google/gemini-2.0-flash-exp:free",
            messages=[
                {"role": "user", "content": message_text}
            ]
        )

        if response.choices is None:
            await message.edit_text(user_text(f"Произошла ошибка, пробуем ещё раз ({count + 1}/3)..."))
        else:
            await message.edit_text(ANSWER_TEXT_FORMAT.format(message=message_text, answer=response.choices[0].message.content))
            return
        
    await message.edit_text(user_text("Произошла ошибка:") + '\n\n' + str(response))


@KGBot.on_message(filters.me & filters.command("ai_set_key"))
@database_decorator
async def set_ai_key_handler(_, message: types.Message, database: Database):
    if len(message.command) < 2:
        return await message.edit_text(user_text("Не указан секретный ключ"))
    
    secret_key = message.command[1]
    await database.set('secret_key', secret_key)
    return await message.edit_text(user_text("Секретный ключ установлен"))
