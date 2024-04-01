import os

from pyrogram import types, filters
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from PIL import Image

from utils.client import KGBot
from utils.env import Env
from utils.utils import user_text


class Help:
    author = 'Koban'
    help_commands = ['gemini']
    modules_description = 'Запрос к Gemini Pro. Для использования надо в .env добавить GEMINI_API_KEY и GEMINI_PROXY\n' \
                          'Прокси нужен для того, чтобы использовать Gemini в странах, где это делать нельзя, если бот ' \
                          'размещен на иностранном сервере, то все должно работать'
    commands_description = {
        'gemini [текст]': 'Запрос к Gemini Pro',
        'gemini [текст] [реплай фото]': 'Запрос к Gemini Pro с картинкой',
    }


@KGBot.on_message(filters.me & filters.command("gemini", KGBot.prefix))
async def gemini_handler(_, message: types.Message):
    await message.edit_text(user_text('Ожидайте...'))

    if message.reply_to_message and message.reply_to_message.photo:
        photo = await message.reply_to_message.download('photo.png')
        gemini_response = await get_gemini_image_response(message.text.split(maxsplit=1)[1], Image.open(photo))
    else:
        if message.reply_to_message and message.reply_to_message.text:
            request_text = message.reply_to_message.text
        else:
            if len(message.command) > 1:
                request_text = message.text.split(maxsplit=1)[1]
            else:
                return await message.edit_text(user_text('Не указано текста для запроса'))

        gemini_response = await get_gemini_text_response(request_text)

    await message.edit_text(gemini_response)


async def get_gemini_text_response(request: str):
    os.environ["http_proxy"] = Env.get('GEMINI_PROXY')
    os.environ["https_proxy"] = Env.get('GEMINI_PROXY')

    genai.configure(api_key=Env.get("GEMINI_API_KEY"))
    model = genai.GenerativeModel()
    response = model.generate_content(request)

    del os.environ["http_proxy"]
    del os.environ["https_proxy"]

    return response.text


async def get_gemini_image_response(request: str, photo: str):
    os.environ["http_proxy"] = Env.get('GEMINI_PROXY')
    os.environ["https_proxy"] = Env.get('GEMINI_PROXY')

    genai.configure(api_key=Env.get("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content(
        [request, photo],
        safety_settings={
            HarmCategory.HARM_CATEGORY_HARASSMENT: 4,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: 4,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: 4,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: 4
        }
    )

    del os.environ["http_proxy"]
    del os.environ["https_proxy"]

    if response.prompt_feedback.block_reason:
        return user_text(f'Ответ заблокирован')

    return response.text