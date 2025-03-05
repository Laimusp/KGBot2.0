import os
import importlib
from core import types, filters
from core.client import KGBot
from utils.utils import get_command_filters


class Help:
    author = 'Koban'
    modules_description = 'Модуль для получения информации о модулях'
    commands_description = {
        'help': 'Получить информацию о модуле',
        'help [module]': 'Получить информацию о модуле',
        'help system.[module]': 'Получить информацию о системном модуле',
    }

@KGBot.on_message(filters.me & filters.command('help'))
async def help_handler(app: KGBot, message: types.Message):
    if len(message.command) > 1:  # информация о модуле
        modules_name = message.text.split(maxsplit=1)[1].replace(' ', '_')
        if modules_name.lower() == 'system':  # Общие данные о системных модулях
            modules_list = [file[:-3] for file in os.listdir('plugins/system') if file.endswith('.py')]
            help_text = f'<b><u>{await app.get_full_name()}</u> | <u>KGBot2.0\n</u></b>' \
                        f'<b>Введите .help [module] чтобы получить информацию о модуле.</b>\n\n' \
                        f'<b>Доступные модули:</b>\n'
            for module_name in modules_list:
                help_info = (await get_modules_help(module_name, app, True)).get('help_commands')
                commands = ' | '.join(help_info) if isinstance(help_info, list) else 'Неизвестно'
                help_text += f'➤ {module_name}: <code>⦑ {commands} ⦒</code>\n'

            help_text += f'\nВсего модулей: <b>{len(modules_list)}</b>'
            await message.edit_text(help_text)

        else:
            if modules_name.startswith('system.'):
                if modules_name.split('.')[1] + '.py' not in os.listdir('plugins/system/'):
                    return await message.edit_text(f'<b><i>Модуль <u>{modules_name}</u></i> не найден</b>')
            else:
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
            help_info = await get_modules_commands(module_name, app)
            commands = ' | '.join(help_info) if isinstance(help_info, list) else 'Неизвестно'
            help_text += f'➤ {module_name}: <code>⦑ {commands} ⦒</code>\n'
        help_text += f'\nВсего модулей: <b>{len(modules_list)}</b>'
        help_text += f'\nЧтобы посмотреть системные модули: <b>.help system:</b>\n'

        await message.edit_text(help_text)


async def get_modules_commands(module_name: str, app: KGBot, system: bool = False) -> list:
    module = importlib.import_module(f'plugins.{module_name}') if not system else importlib.import_module(f'plugins.system.{module_name}')
    handlers = [item for item in module.__dict__.values() if hasattr(item, 'handlers')]
    handlers_info = []
    for handler in handlers:
        if handler.handlers:
            _handler, group = handler.handlers[0]
            if _handler in app.dispatcher.groups[0]:
                command_filter = get_command_filters(_handler.filters)
                if command_filter:
                    handlers_info.extend(list(command_filter.commands))

    return handlers_info or 'Нет команд'


async def get_modules_help(module_name: str, app: KGBot, system: bool = False) -> dict:
    """Получить информацию о модуле (Поля класса Help)"""
    module = importlib.import_module(f'plugins.{module_name}') if not system else importlib.import_module(f'plugins.system.{module_name}')
    help_class = getattr(module, 'Help', None)
    return {
        'author': getattr(help_class, 'author', 'Неизвестно'),
        'help_commands': await get_modules_commands(module_name, app, system),
        'modules_description': getattr(help_class, 'modules_description', 'Неизвестно'),
        'commands_description': getattr(help_class, 'commands_description', {}),
    }