import g4f
from pyrogram import filters, types
from utils.client import KGBot


REQUEST_LAYOUT = '<b>Запрос:</b>\n<pre>{}</pre>\n\n'
ANSWER_LAYOUT = '<b>Ответ:</b>\n<pre>{}</pre>\n\n'


class Help:
    author = 'Koban'
    help_commands = ['gpt']
    modules_description = 'Вопрос-ответ ChatGPT-3.5 без использования API-ключа'
    commands_description = {
        'gpt [запрос]': 'Сделать запрос ChatGPT-3.5'
    }


@KGBot.on_message(filters.me & filters.command('gpt', KGBot.prefix))
async def gpt_request_handler(_, message: types.Message):
    if len(split_text := message.text.split(maxsplit=1)) == 1:
        return await message.edit_text('<b><i>Вы забыли указать запрос</i></b>')

    await message.edit_text('<b><i>Ожидаем ответ...</i></b>')

    _, request_text = split_text
    response_text = await g4f.ChatCompletion.create_async(
        model=g4f.models.default,
        messages=[{"role": "user", "content": request_text}]
    )

    await message.edit_text(REQUEST_LAYOUT.format(request_text) + ANSWER_LAYOUT.format(response_text))


