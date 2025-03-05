import time
from core import filters, types
from core.client import KGBot


class Help:
    author = 'Koban'
    modules_description = 'Получить пинг'
    commands_description = {
        'ping (p)': 'Пингуем, пацаны'
    }


@KGBot.on_message(filters.command(['ping', 'p']) & filters.me)
async def ping_handler(_, message: types.Message):
    ping_time = time.time() - time.mktime(message.date.timetuple())
    await message.edit_text(f'<b>Пинг: <code>{ping_time * 100:.2f}</code> мс</b>')