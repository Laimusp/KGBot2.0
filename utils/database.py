import logging
import os
import json
from datetime import datetime
import aiofiles
import aiofiles.os
import asyncio

class Database(dict):
    def __init__(self, location: str, main_key: str = "__main__"):
        super().__init__()
        self.database_calling = 0
        self.main_key = main_key
        self.location = location

    async def load(self):
        try:
            async with aiofiles.open(self.location, 'r', encoding='utf-8') as f:
                content = await f.read()
                data = json.loads(content)
                self.update(data)
        except FileNotFoundError:
            self.clear()

    async def save(self):
        dir_path = os.path.dirname(self.location)
        if dir_path and not await aiofiles.os.path.exists(dir_path):
            await aiofiles.os.makedirs(dir_path, exist_ok=True)
        
        async with aiofiles.open(self.location, 'w', encoding='utf-8') as f:
            content = json.dumps(dict(self), ensure_ascii=False, indent=4)
            await f.write(content)
        return True

    async def set(self, key, value):
        self.setdefault(self.main_key, {})[key] = value
        return await self.save()

    async def get(self, key, default=None):
        self.database_calling += 1
        if self.database_calling % 15 == 0:
            await self.make_backup()

        main_dict = super().get(self.main_key, {})
        return main_dict.get(key, default)

    async def pop(self, key):
        main_dict = self.setdefault(self.main_key, {})
        popped = main_dict.pop(key, None)
        await self.save()
        return popped

    async def reset(self):
        self.clear()
        await self.save()
        return True

    async def make_backup(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_filename = f"{self.location}.{timestamp}.bak"

        data = dict(self)
        
        async with aiofiles.open(backup_filename, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data, indent=4, ensure_ascii=False))

        backup_dir = os.path.dirname(self.location) or '.'
        loop = asyncio.get_event_loop()
        backup_files = await loop.run_in_executor(
            None,
            lambda: [os.path.join(backup_dir, f) for f in os.listdir(backup_dir) if f.endswith('.bak')]
        )

        if len(backup_files) > 3:
            oldest_backup = min(backup_files, key=lambda f: os.path.getctime(f))
            await aiofiles.os.remove(oldest_backup)

    def change_root(self, main_key):
        self.main_key = main_key