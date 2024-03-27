import os
from importlib import import_module
from pyrogram import types, filters
from utils.client import KGBot


@KGBot.on_message(filters.command('help', KGBot.prefix))
async def help_handler(app: KGBot, message: types.Message):
    if len(message.command) > 1:  # информация о модуле
        modules_name = message.text.split(maxsplit=1)[1].replace(' ', '_')
        if modules_name + '.py' not in os.listdir('plugins/'):
            return await message.edit_text(f'<b><i>Модуль <u>{modules_name}</u></i> не найден</b>')

        modules_help = await get_modules_help(modules_name)
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
            help_info = (await get_modules_help(module_name)).get('help_commands')
            commands = ' | '.join(help_info) if isinstance(help_info, list) else 'Неизвестно'
            help_text += f'➤ {module_name}: <code>⦑ {commands} ⦒</code>\n'
        help_text += f'\nВсего модулей: <b>{len(modules_list)}</b>'

        await message.edit_text(help_text)


async def get_modules_help(modules_name: str) -> dict:
    """Получить информацию о модуле (Поля класса Help)"""
    module = import_module(f'plugins.{modules_name}')
    help_class = getattr(module, 'Help', None)
    return {
        'author': getattr(help_class, 'author', 'Неизвестно'),
        'help_commands': getattr(help_class, 'help_commands', 'Неизвестно'),
        'modules_description': getattr(help_class, 'modules_description', 'Неизвестно'),
        'commands_description': getattr(help_class, 'commands_description', {}),
    }