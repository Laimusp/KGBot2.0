from utils import database


def database_decorator(pyrogram_func):
    async def wrapper(*args, **kwargs):
        database.change_root(pyrogram_func.__globals__["__name__"])
        return await pyrogram_func(*args, database=database, **kwargs)

    return wrapper