import importlib
import os
from collections import defaultdict

from core import filters, types
from core.client import KGBot
from utils.utils import user_text, get_command_filters

alias_info = defaultdict(list)


class Help:
    author = 'Koban'
    modules_description = 'Модуль для создания алиасов (сокращения команд)'
    commands_description = {
        'alias [команда] [сокращение]': 'Создание алиаса',
        'unalias [команда]': 'Удаление алиаса',
        'show_alias': 'Показать список алиасов'
    }


@KGBot.on_message(filters.me & filters.command("alias"))
async def create_alias_handler(app: KGBot, message: types.Message):
    if len(message.command) < 3:
        return await message.edit_text(user_text('Недостаточно аргументов'))

    _, command_name, alias = message.command

    for root, dirs, files in os.walk('plugins/'):
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                relative_path = os.path.relpath(root, 'plugins/')
                module_name = os.path.splitext(file)[0]
                
                if relative_path == '.':
                    full_module_name = f"plugins.{module_name}"
                else:
                    full_module_name = f"plugins.{relative_path.replace(os.sep, '.')}." + module_name
                
                module = importlib.import_module(full_module_name)
                handlers = [item for item in module.__dict__.values() if hasattr(item, 'handlers')]
                for handler in handlers:
                    if handler.handlers:
                        _handler, group = handler.handlers[0]
                        if _handler in app.dispatcher.groups[0]:
                            command_filter = get_command_filters(_handler.filters)
                            if command_filter and command_name.lower() in command_filter.commands:
                                command_filter.commands.add(alias.lower())
                                alias_info[command_name.lower()].append(alias.lower())
                                return await message.edit_text(user_text('Алиас успешно создан'))

    await message.edit_text(user_text('Не удалось создать алиас'))


# TODO удаление алиасов

@KGBot.on_message(filters.me & filters.command("show_alias"))
async def show_alias_handler(_, message: types.Message):
    if alias_info:
        text = 'Алиасы:\n'
        for command, aliases in alias_info.items():
            text += f'# {command} - {", ".join(aliases)}\n'

        await message.edit_text(user_text(text))
    else:
        await message.edit_text(user_text('Алиасов нет'))

