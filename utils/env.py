import os
from dotenv import load_dotenv
import aiofiles


class Env:
    env_file = '.env'

    @classmethod
    async def get(cls, key, default=None):
        """Получает значение переменной окружения по ключу."""
        await cls._load_env_if_needed()  # Загрузка .env, если требуется
        return os.getenv(key, default)

    @classmethod
    async def set(cls, key, value):
        """Устанавливает значение переменной окружения."""
        os.environ[key] = value

        async with aiofiles.open(cls.env_file, "r") as f:
            lines = await f.readlines()

        new_env_file_text = ''
        for line in lines:
            if not line.startswith(f"{key}="):
                new_env_file_text += line

        async with aiofiles.open(cls.env_file, "w") as f:
            await f.write(new_env_file_text)

        async with aiofiles.open(cls.env_file, "a") as f:
            await f.write(f"{key}={value}\n")

    @classmethod
    async def delete(cls, key):
        """Удаляет переменную окружения."""
        if key in os.environ:
            del os.environ[key]

        # Удаление из файла .env (более сложная операция)
        async with aiofiles.open(cls.env_file, "r") as f:
            lines = await f.readlines()

        async with aiofiles.open(cls.env_file, "w") as f:
            for line in lines:
                if not line.startswith(f"{key}="):
                    await f.write(line)

    @classmethod
    async def get_list(cls) -> dict:
        """Возвращает все переменные из .env в виде словаря."""
        await cls._load_env_if_needed()

        env_dict = {}
        async with aiofiles.open(cls.env_file, "r") as f:
            lines = await f.readlines()
            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):  # Игнорирование пустых строк и комментариев
                    key, value = line.split("=", 1)
                    env_dict[key] = value

        return env_dict

    @classmethod
    async def create_env_file_if_not_exists(cls):
        """Создает файл .env, если он не существует."""
        if not os.path.exists(cls.env_file):
            async with aiofiles.open(cls.env_file, "w") as f:
                await f.write("")

        await cls._load_env_if_needed()

    @classmethod
    async def _load_env_if_needed(cls):
        """Загружает .env, если он еще не загружен."""
        if not hasattr(cls, '_env_loaded'):
            load_dotenv(cls.env_file, override=True)
            cls._env_loaded = True