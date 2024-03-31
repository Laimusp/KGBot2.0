import importlib
import os
from collections import defaultdict

from pyrogram import filters, types
from utils.client import KGBot
from utils.utils import user_text


alias_info = defaultdict(list)


@KGBot.on_message(filters.me & filters.command("alias", KGBot.prefix))
async def create_alias_handler(app: KGBot, message: types.Message):
    if len(message.command) < 3:
        return await message.edit_text(user_text('Недостаточно аргументов'))

    _, command_name, alias = message.command

    for module_name in [item[:-3] for item in os.listdir('plugins/') if item.endswith('.py')]:
        module = importlib.import_module(f'plugins.{module_name}')
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

@KGBot.on_message(filters.me & filters.command("show_alias", KGBot.prefix))
async def show_alias_handler(_, message: types.Message):
    if alias_info:
        text = 'Алиасы:\n'
        for command, aliases in alias_info.items():
            text += f'# {command} - {", ".join(aliases)}\n'

        await message.edit_text(user_text(text))
    else:
        await message.edit_text(user_text('Алиасов нет'))


def get_command_filters(_filters):
    while isinstance(_filters, filters.AndFilter):
        if isinstance(_filters.base, filters.AndFilter):
            _filters = _filters.base
            continue

        base_flt_name = _filters.base.__class__.__name__
        other_flt_name = _filters.other.__class__.__name__
        return _filters.base if 'CommandFilter' in base_flt_name else _filters.other if 'CommandFilter' in other_flt_name else None
