from utils import db


def database_decorator(pyrogram_func):
    async def wrapper(*args, **kwargs):
        db.change_root(pyrogram_func.__globals__["__name__"])
        return await pyrogram_func(*args, db=db, **kwargs)

    return wrapper