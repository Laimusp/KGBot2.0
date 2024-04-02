# основные импорты, такие как фильтры, типы и сам класс Client (KGBot)

from pyrogram import types, filters
from utils.client import KGBot
from utils.utils import user_text


class Help:  # класс для help'а, имеет 4 поля
    author = 'Koban'  # автор
    help_commands = ['ex', 'ex2']  # команды, который будут показываться в .help, можно не указывать (будет Неизвестно)
    modules_description = 'Описание модулей'  # описание модулей
    commands_description = {
        'ex': 'Пример использования',  # точное описание каждой команды
        'ex2': 'Пример использования 2'
    }

    # в будущем help_commands будет изменен, чтобы он напрямую получал команды из хендлера, но пока так
    # позже будет добавлена работа с базой данных


@KGBot.on_message(filters.me & filters.command(["ex"], KGBot.prefix))  # указываем фильтры и префикс
async def example_handler(app: KGBot, message: types.Message):
    # Здесь основная логика кода
    # в данном случае я заменил бы app на _, так как он не используется, но для примера пусть будет так
    await message.edit_text(user_text(message.from_user.first_name))


@KGBot.on_message(filters.me & filters.command(["ex"], KGBot.prefix))
async def example2_handler(app: KGBot, message: types.Message):
    # Здесь основная логика еще одного хендлера
    await message.edit_text(user_text(message.from_user.last_name))