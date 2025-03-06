import os
import sys
from core import types, filters
from core.client import KGBot
from meval import meval


class CustomStdout:
    def __init__(self):
        self.output = ''

    def write(self, message: str):
        self.output += message


@KGBot.on_message(filters.me & filters.command('exec'))
async def execute_file(_, message: types.Message):
    if len(message.command) < 2:
        return await message.reply_text('Введите путь к файлу')
    
    file_path = message.command[1]
    if not os.path.exists(file_path):
        return await message.reply_text('Файл не найден')
    
    with open(file_path, 'r', encoding='utf-8') as file:
        code = file.read()

    old_stdout = sys.stdout
    sys.stdout = CustomStdout()

    output = result = None

    try:
        result = await meval(code, globals())
        output = sys.stdout.output.strip()
    except Exception as e:
        return await message.reply_text(f'Ошибка при выполнении файла: {e}')
    finally:
        sys.stdout = old_stdout

    if result and output:
        return await message.reply_text(f'Результат выполнения файла:\n{result}\n\nВывод:\n{output}')
    elif result:
        return await message.reply_text(f'Результат выполнения файла:\n{result}')
    elif output:
        return await message.reply_text(f'Вывод:\n{output}')
    else:
        return await message.reply_text('Файл выполнен успешно - ничего не выведено и не возвращено')
