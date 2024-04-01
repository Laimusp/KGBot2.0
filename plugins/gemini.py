import os

from pyrogram import types, filters
import google.generativeai as genai

from utils.client import KGBot
from utils.env import Env
from utils.utils import user_text


class Help:
    author = 'Koban'
    help_commands = ['gemini']
    modules_description = 'Запрос к Gemini Pro. Для использования надо в .env добавить GEMINI_API_KEY и GEMINI_PROXY, если не работает'
    commands_description = {
        'gemini [текст]': 'Запрос к Gemini Pro'
    }


@KGBot.on_message(filters.me & filters.command("gemini", KGBot.prefix))
async def gemini_handler(_, message: types.Message):
    await message.edit_text(user_text('Ожидайте...'))

    gemini_response = await get_gemini_response(message.text.split(maxsplit=1)[1])
    await message.edit_text(gemini_response)


async def get_gemini_response(request: str):
    os.environ["http_proxy"] = Env.get('GEMINI_PROXY')
    os.environ["https_proxy"] = Env.get('GEMINI_PROXY')

    genai.configure(api_key=Env.get("GEMINI_API_KEY"))
    model = genai.GenerativeModel()
    response = model.generate_content(request)

    del os.environ["http_proxy"]
    del os.environ["https_proxy"]

    return response.text