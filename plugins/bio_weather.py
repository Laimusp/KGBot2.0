import asyncio

import requests

from pyrogram import types, filters
from utils.client import KGBot
from utils.utils import user_text

CITY = "Москва"
OPENWEATHER_API_KEY = ""
OPENWEATHER_URL = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&lang=ru&units=metric&appid={OPENWEATHER_API_KEY}"

AUTOEDIT_BIO_ON = False


async def bio_weather(app: KGBot):
    while AUTOEDIT_BIO_ON:
        response = requests.get(OPENWEATHER_URL).json()

        city = response["name"]
        description = response["weather"][0]["description"]
        cur_temp = round(float(response["main"]["temp"]))
        feels_like = round(float(response["main"]["feels_like"]))

        text = f'Сейчас в городе {city} {description}.\nТемпература {cur_temp}℃, ощущается как {feels_like}℃'
        await app.update_profile(bio=text)

        await asyncio.sleep(300)


@KGBot.on_message(filters.me & filters.command("bio_weather", KGBot.prefix))
async def bio_weather_handler(app: KGBot, message: types.Message):
    global AUTOEDIT_BIO_ON
    if AUTOEDIT_BIO_ON:
        AUTOEDIT_BIO_ON = False
        await message.edit_text(user_text('Автоматическая редакция био отключена'))
        await app.update_profile(bio='')
    else:
        AUTOEDIT_BIO_ON = True
        await message.edit_text(user_text('Автоматическая редакция био включена'))
        await asyncio.create_task(bio_weather(app))