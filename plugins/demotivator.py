# создай модуль демотиватор (когда берется картинка в рамку, а внизу дописывается текст)
import os

from PIL import Image, ImageDraw, ImageFont

from pyrogram import types, filters
from utils.client import KGBot
from utils.utils import user_text


@KGBot.on_message(filters.me & filters.command("demotivator", KGBot.prefix))
async def demotivator_handler(_, message: types.Message):
    if len(message.text.split()) < 2:
        return await message.edit_text(user_text("Недостаточно аргументов"))

    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.edit_text(user_text("Вы не указали фотографию"))

    photo = await message.reply_to_message.download(file_name="photo.png")
    await message.edit_text(user_text("В процессе..."))

    demotivator_photo = get_demotivator_photo(message.text.split(maxsplit=1)[1], photo)
    await message.reply_photo(demotivator_photo)
    await message.delete()

    os.remove(photo)


def get_demotivator_photo(message_text: str, photo: str):
    if '\n' in message_text:
        big_text, small_text = message_text.split('\n')
    else:
        big_text = message_text
        small_text = ""

    big_font = ImageFont.truetype('times.ttf', 72, encoding='utf-8')
    small_font = ImageFont.truetype('times.ttf', 48, encoding='utf-8')

    background = Image.new("RGB", (1400, 1050), "black")
    img = Image.open(photo)
    img = img.resize((1100, 700))

    photo_coord = (background.size[0] // 2 - img.size[0] // 2, background.size[1] // 3 + 50 - img.size[1] // 2)
    background.paste(img, photo_coord)

    draw = ImageDraw.Draw(background)
    draw.rectangle((photo_coord[0] - 10, photo_coord[1] - 10, photo_coord[0] + img.size[0] + 10,
                    photo_coord[1] + img.size[1] + 10), outline="white", width=3)

    _, _, *small_text_size = small_font.getbbox(small_text)
    _, _, *big_text_size = big_font.getbbox(big_text)

    big_text_coord = (
        background.size[0] // 2 - big_text_size[0] // 2, img.size[1] + photo_coord[1] + big_text_size[1] // 2)
    small_text_coord = (
        background.size[0] // 2 - small_text_size[0] // 2, big_text_coord[1] + small_text_size[1] // 2 + 80)

    draw.text(small_text_coord, small_text, fill="white", font=small_font)
    draw.text(big_text_coord, big_text, fill="white", font=big_font)

    background.save("photo.png")
    return "photo.png"
