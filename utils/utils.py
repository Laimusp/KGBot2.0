import importlib
import os
from collections import defaultdict

from pyrogram import filters

from utils.client import KGBot


def user_text(text: str):
    return f'<b><i>{text}</i></b>'


def get_command_filters(_filters):
    """Получить фильтр с командами из связки фильтров"""
    while isinstance(_filters, filters.AndFilter):
        if isinstance(_filters.base, filters.AndFilter):
            _filters = _filters.base
            continue

        base_flt_name = _filters.base.__class__.__name__
        other_flt_name = _filters.other.__class__.__name__
        return _filters.base if 'CommandFilter' in base_flt_name else _filters.other if 'CommandFilter' in other_flt_name else None

    return _filters
