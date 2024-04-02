import importlib
import os
from importlib import import_module
from pyrogram import types, filters
from utils.client import KGBot
from utils.utils import get_command_filters


@KGBot.on_message(filters.command('help', KGBot.prefix))
async def help_handler(app: KGBot, message: types.Message):
    if len(message.command) > 1:  # информация о модуле
        modules_name = message.text.split(maxsplit=1)[1].replace(' ', '_')
        if modules_name + '.py' not in os.listdir('plugins/'):
            return await message.edit_text(f'<b><i>Модуль <u>{modules_name}</u></i> не найден</b>')

        modules_help = await get_modules_help(modules_name, app)
        help_text = f'<b>Информация о модуле <u>{modules_name}</u></b>:\n\n' \
                    f'<b>Автор:</b> <pre>{modules_help["author"]}</pre>\n\n' \
                    f'<b>Описание:</b>\n<pre>{modules_help["modules_description"]}</pre>\n\n' \
                    f'<b>Команды:</b>\n'
        for command, des in modules_help['commands_description'].items():
            help_text += f'<pre>{command}</pre>\n\t\t⤷\t{des}\n'

        if not modules_help['commands_description']:
            help_text += '<pre>Неизвестно</pre>'

        await message.edit_text(help_text)

    else:  # просто общий хелп
        modules_list = [file[:-3] for file in os.listdir('plugins/') if file.endswith('.py')]
        help_text = f'<b><u>{await app.get_full_name()}</u> | <u>KGBot2.0\n</u></b>' \
                    f'<b>Введите .help [module] чтобы получить информацию о модуле.</b>\n\n' \
                    f'<b>Доступные модули:</b>\n'
        for module_name in modules_list:
            help_info = (await get_modules_help(module_name, app)).get('help_commands')
            commands = ' | '.join(help_info) if isinstance(help_info, list) else 'Неизвестно'
            help_text += f'➤ {module_name}: <code>⦑ {commands} ⦒</code>\n'
        help_text += f'\nВсего модулей: <b>{len(modules_list)}</b>'

        await message.edit_text(help_text)


async def get_modules_commands(module_name: str, app: KGBot) -> list:
    module = importlib.import_module(f'plugins.{module_name}')
    handlers = [item for item in module.__dict__.values() if hasattr(item, 'handlers')]
    handlers_info = []
    for handler in handlers:
        if handler.handlers:
            _handler, group = handler.handlers[0]
            if _handler in app.dispatcher.groups[0]:
                command_filter = get_command_filters(_handler.filters)
                if command_filter:
                    handlers_info.append(list(command_filter.commands)[0])

    return handlers_info or 'Неизвестно'


async def get_modules_help(module_name: str, app: KGBot) -> dict:
    """Получить информацию о модуле (Поля класса Help)"""
    module = import_module(f'plugins.{module_name}')
    help_class = getattr(module, 'Help', None)
    return {
        'author': getattr(help_class, 'author', 'Неизвестно'),
        'help_commands': await get_modules_commands(module_name, app),
        'modules_description': getattr(help_class, 'modules_description', 'Неизвестно'),
        'commands_description': getattr(help_class, 'commands_description', {}),
    }