import os
from dotenv import load_dotenv


class Env:
    env_file = '.env'

    @classmethod
    def get(cls, key, default=None):
        """Получает значение переменной окружения по ключу."""
        cls._load_env_if_needed()  # Загрузка .env, если требуется
        return os.getenv(key, default)

    @classmethod
    def set(cls, key, value):
        """Устанавливает значение переменной окружения."""
        os.environ[key] = value

        # Обновление файла .env
        with open(cls.env_file, "a") as f:
            f.write(f"{key}={value}\n")

    @classmethod
    def delete(cls, key):
        """Удаляет переменную окружения."""
        if key in os.environ:
            del os.environ[key]

        # Удаление из файла .env (более сложная операция)
        with open(cls.env_file, "r") as f:
            lines = f.readlines()

        with open(cls.env_file, "w") as f:
            for line in lines:
                if not line.startswith(f"{key}="):
                    f.write(line)

    @classmethod
    def get_list(cls) -> dict:
        """Возвращает все переменные из .env в виде словаря."""
        cls._load_env_if_needed()

        env_dict = {}
        with open(cls.env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):  # Игнорирование пустых строк и комментариев
                    key, value = line.split("=", 1)
                    env_dict[key] = value

        return env_dict

    @classmethod
    def create_env_file_if_not_exists(cls):
        """Создает файл .env, если он не существует."""
        if not os.path.exists(cls.env_file):
            with open(cls.env_file, "w") as f:
                f.write("# KEY=VALUE\n")

        cls._load_env_if_needed()

    @classmethod
    def _load_env_if_needed(cls):
        """Загружает .env, если он еще не загружен."""
        if not hasattr(cls, '_env_loaded'):
            load_dotenv(cls.env_file)
            cls._env_loaded = True