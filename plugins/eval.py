import re
import sys
from html import escape
import traceback

from pyrogram import types, filters
from meval import meval
from utils.client import KGBot


class Help:
    author = 'Koban'
    help_commands = ['e']
    modules_description = 'Модуль, который выполняет код на языке программирования Python'
    commands_description = {
        '.e': 'Выполнить код по реплаю',
        '.e [code]': 'Выполнить код'
    }


class CustomStdout:
    def __init__(self):
        self.output = ''

    def write(self, message: str):
        self.output += message


code_model = '<b>Код:</b>\n<pre>{}</pre>\n\n'
return_model = '<b>Возвращено:</b>\n<pre>{}</pre>\n\n'
print_model = '<b>Вывод:</b>\n<pre>{}</pre>\n\n'
error_model = '<b>Ошибка:</b>\n<pre>{}</pre>\n\n'


@KGBot.on_edited_message(filters.regex(r'(?<=Код:)(.*)(?=\n(?:Вывод:|Возвращено:|Ошибка:))', re.DOTALL) & filters.me)
@KGBot.on_edited_message(filters.regex(r'(?<=Код:)(.*)', re.DOTALL) & filters.me)
@KGBot.on_message(filters.command('e', '.') & filters.me)
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

    old_stdout = sys.stdout
    sys.stdout = CustomStdout()
    error_output = returned_result = None

    try:
        returned_result = await meval(code_text, globals(), **get_variables(message, app))
    except Exception:
        error_output = str(traceback.format_exc())

    printed_result = sys.stdout.output
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
        'app': app
    }
