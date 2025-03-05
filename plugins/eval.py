import asyncio
import re
import sys
import traceback
from html import escape
from meval import meval
from core import types, filters
from core.client import KGBot
from utils.utils import user_text


class Help:
    author = 'Koban'
    modules_description = 'Модуль, который выполняет код на языке программирования Python'
    commands_description = {
        'e': 'Выполнить код по реплаю',
        'e [code]': 'Выполнить код'
    }


class CustomStdout:
    def __init__(self):
        self.output = ''

    def write(self, message: str):
        self.output += message


class NewCustomInput:
    def __init__(self, client: KGBot = None, message: types.Message = None):
        self.client = client
        self.message = message

    async def __call__(self, message_text: str = '', *args, **kwargs):
        new_message = await self.message.reply_text(user_text(f'Программа ожидает ввода...\n\n{message_text}').strip())
        while True:
            message_id = [item async for item in self.client.get_chat_history(self.message.chat.id, limit=1)][0].id
            message = await self.client.get_messages(self.message.chat.id, message_id)
            if message.text and message.reply_to_message and message.reply_to_message.id == new_message.id:
                await new_message.delete()
                await message.delete()
                return message.text

            await asyncio.sleep(1)


code_model = '<b>Код:</b>\n<pre>{}</pre>\n\n'
return_model = '<b>Возвращено:</b>\n<pre>{}</pre>\n\n'
print_model = '<b>Вывод:</b>\n<pre>{}</pre>\n\n'
error_model = '<b>Ошибка:</b>\n<pre>{}</pre>\n\n'


@KGBot.on_edited_message(filters.regex(r'(?<=Код:)(.*)(?=\n(?:Вывод:|Возвращено:|Ошибка:))', re.DOTALL) & filters.me)
@KGBot.on_edited_message(filters.regex(r'(?<=Код:)(.*)', re.DOTALL) & filters.me)
@KGBot.on_message(filters.command('e') & filters.me)
async def eval_handler(app: KGBot, message: types.Message):
    if message.command:  # отправленное сообщение
        if not (reply := message.reply_to_message) and len(message.command) == 1:
            return await message.edit_text('<b><i>Вы не указали сам <u>код</u></i></b>')

        if reply and (len(message.command) == 1):
            code_text = get_code(reply.text)
        else:
            code_text = message.text.split(maxsplit=1)[1].strip()
    else:  # отредактировано
        code_text = get_code(message.text)

    code_text = code_text.replace('input', 'await input')
    old_stdout = sys.stdout
    sys.stdout = CustomStdout()
    error_output = returned_result = None

    try:
        returned_result = await meval(code_text, globals(), **get_variables(message, app))
    except Exception:
        error_output = str(traceback.format_exc())

    printed_result = sys.stdout.output.strip()
    code_text = code_text.replace('await input', 'input')
    if returned_result and printed_result:
        result_output = code_model.format(escape(code_text)) + return_model.format(escape(str(returned_result))) + \
                        print_model.format(escape(printed_result))
    elif returned_result:
        result_output = code_model.format(escape(code_text)) + return_model.format(escape(str(returned_result)))
    elif printed_result:
        result_output = code_model.format(escape(code_text)) + print_model.format(escape(printed_result))
    else:
        result_output = code_model.format(escape(code_text))

    sys.stdout = old_stdout
    if error_output:  # если была ошибка
        result_output += error_model.format(escape(error_output))

    await message.edit_text(result_output)


def get_code(text: str) -> str:
    text_info = re.search(r'(?<=Код:)(.*?)(?=\n(?:Вывод:|Возвращено:|Ошибка:))', text, re.DOTALL)
    if text_info is not None:
        return text_info.group(1).strip()

    text_info = re.search(r'(?<=Код:)(.*)', text, re.DOTALL)
    if text_info is not None:
        return text_info.group(1).strip()

    return text


def get_variables(message: types.Message, app: KGBot) -> dict:
    return {
        'msg': message,
        'message': message,
        'reply': message.reply_to_message,
        'app': app,
        'input': NewCustomInput(client=app, message=message)
    }
