from core import types, filters
from core.client import KGBot
from utils.env import Env
from utils.utils import user_text


class Help:
    author = 'Koban'
    modules_description = 'Модуль для работы с переменными окружения'
    commands_description = {
        'env_add': 'Добавить переменную в .env',
        'env_del': 'Удалить переменную из .env',
        'env_get': 'Получить значение переменной из.env',
        'env_list': 'Получить список переменных окружения'
    }


@KGBot.on_message(filters.me & filters.command("env_add"))
async def env_add_handler(_, message: types.Message):
    if len(message.text.split()) < 3:
        return await message.edit_text(user_text("Формат: env_add <ключ> <значение>"))

    _, key, value = message.command

    await Env.set(key.upper(), value)

    await message.edit_text(f"Значение <b>{key}</b> успешно добавлено в .env")


@KGBot.on_message(filters.me & filters.command("env_del"))
async def env_del_handler(_, message: types.Message):
    if len(message.text.split()) < 2:
        return await message.edit_text(user_text("Формат: env_del <ключ>"))

    _, key = message.command

    await Env.delete(key.upper())

    await message.edit_text(user_text(f"Значение <b>{key}</b> успешно удалено из .env"))


@KGBot.on_message(filters.me & filters.command("env_get"))
async def env_get_handler(_, message: types.Message):
    if len(message.text.split()) < 2:
        return await message.edit_text(user_text("Формат: env_get <ключ>"))

    _, key = message.command

    value = await Env.get(key.upper())
    if value is None:
        return await message.edit_text(user_text(f"Значение <b>{key}</b> не найдено в .env"))

    await message.edit_text(f"<b>{key}</b> = <code>{value}</code>")


@KGBot.on_message(filters.me & filters.command("env_list"))
async def env_list_handler(_, message: types.Message):
    env_info = await Env.get_list()
    if not env_info:
        return await message.edit_text(user_text("Нет переменных в .env"))

    env_text = user_text('Переменные в .env:\n')
    for key, value in env_info.items():
        env_text += f"➤ <b>{key}</b> = <code>{value}</code>\n"

    await message.edit_text(env_text)
