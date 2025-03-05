import os
import asyncio

from pyrogram import idle
from pyrogram.enums.parse_mode import ParseMode

from core.client import KGBot
from utils import log_setting, db
from utils.env import Env


async def main():
    log_setting.configure_logging()
    Env.create_env_file_if_not_exists()

    api_id = api_hash = None
    if not os.path.exists('my_account.session'):
        api_id = input('Введите API_ID: ')
        api_hash = input('Введите API_HASH: ')

    app = KGBot('my_account', api_id=api_id, api_hash=api_hash, plugins=dict(root='plugins'), parse_mode=ParseMode.HTML)

    await app.start()
    await idle()
    await app.stop()

if __name__ == '__main__':
    asyncio.run(main())
