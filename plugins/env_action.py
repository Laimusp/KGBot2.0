from pyrogram import types, filters
from utils.client import KGBot
from utils.env import Env
from utils.utils import user_text


class Help:
    author = 'Koban'
    help_commands = ['env_add', 'env_del', 'env_get', 'env_list']
    modules_description = 'Модуль для работы с переменными окружения'
    commands_description = {
        'env_add': 'Добавить переменную в .env',
        'env_del': 'Удалить переменную из .env',
        'env_list': 'Получить список переменных окружения'
    }


@KGBot.on_message(filters.me & filters.command("env_add", KGBot.prefix))
async def env_add_handler(_, message: types.Message):
    if len(message.text.split()) < 3:
        return await message.edit_text(user_text("Формат: env_add <ключ> <значение>"))

    _, key, value = message.command

    Env.set(key.UPPER(), value)

    await message.edit_text(f"Значение {key} успешно добавлено в .env")


@KGBot.on_message(filters.me & filters.command("env_del", KGBot.prefix))
async def env_del_handler(_, message: types.Message):
    if len(message.text.split()) < 2:
        return await message.edit_text(user_text("Формат: env_del <ключ>"))

    _, key = message.command

    Env.delete(key.UPPER())

    await message.edit_text(user_text("Значение {key} успешно удалено из .env"))


@KGBot.on_message(filters.me & filters.command("env_get", KGBot.prefix))
async def env_get_handler(_, message: types.Message):
    if len(message.text.split()) < 2:
        return await message.edit_text(user_text("Формат: env_get <ключ>"))

    _, key = message.command

    value = Env.get(key.UPPER())
    if value is None:
        return await message.edit_text(user_text(f"Значение {key} не найдено в .env"))

    await message.edit_text(f"<b>{key}</b> = <code>{value}</code>")


@KGBot.on_message(filters.me & filters.command("env_list", KGBot.prefix))
async def env_list_handler(_, message: types.Message):
    env_info = Env.get_list()
    if not env_info:
        return await message.edit_text(user_text("Нет переменных в .env"))

    env_text = user_text('Переменные в .env:\n')
    for key, value in env_info.items():
        env_text += f"➤ <b>{key}</b> = <code>{value}</code>\n"

    await message.edit_text(env_text)
