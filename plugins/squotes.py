import io
import os
import json
import base64
import requests
from typing import List

from core import filters
from core.types import Message, MessageEntity
from core.types import Audio, Sticker

from core.client import KGBot

__module_info__ = {
    'strings': {
        'ru': {
            'no_args': "Нет аргументов или реплая",
            'loading': "<b>[SQuotes]</b> Обработка...",
            'module_error': "<b>[SQuotes]</b> Ошибка модуля <code>{}</code>.",
            'api_request': "<b>[SQuotes]</b> Ожидание API...",
            'api_error': "<b>[SQuotes]</b> Ошибка API",
            'sending': "<b>[SQuotes]</b> Отправка...",
            'deleted_account': 'Удалённый аккаунт',
        },
    }
}


class Help:
    author = 'Koban, Pelmeshke, Fl1yd'
    modules_description = 'Легендарные квотесы от Флийда, переделанные Пельменем и доделанные мной'
    commands_description = {
        'sq [текст]*': 'Создать квотес, если указать текст, то исходный текст заменится на указанный вами',
        'rsq [кол-во N]': 'Создать квотес из реплаев',
        'msq [кол-во N]': 'Создать квотес от указанного реплаем до N вверх',
    }


def get_string(string_id, *args, **kwargs):
    return __module_info__["strings"]["ru"].get(string_id, 'None').format(*args, **kwargs)


API_ENDPOINT = "https://quotes.fl1yd.su/generate"


@KGBot.on_message(filters.me & filters.command('sq'))
async def squotes_handler(app, message: Message):
    args = message.command[1:]
    if '!file' in args:
        is_file = True
        args.remove('!file')
    else:
        is_file = False

    args = ' '.join(args)
    reply = message.reply_to_message
    if not (args or reply):
        return await message.edit(get_string('no_args'))

    await message.edit(get_string('loading'))

    try:
        payload = {'messages': [
            pack_message(
                *(await parse_messages(app, message, args, reply))
            )
        ]}

    except Exception as e:
        return await message.edit(get_string('module_error', error=repr(e)))

    await message.edit(get_string('api_request'))
    r = await _api_request(payload)
    open("payload.json", "w", encoding='utf8').write(json.dumps(payload, indent=4, ensure_ascii=False))

    if r.status_code != 200:
        return await message.edit(get_string('api_error'))

    quote = io.BytesIO(r.content)
    quote.name = "SQuote.webp"

    await message.edit(get_string('sending'))
    if is_file:
        await app.send_document(
            message.chat.id, quote,
            force_document=True,
            reply_to_message_id=(reply or message).id
        )
    else:
        await app.send_sticker(message.chat.id, quote, reply_to_message_id=(reply or message).id)

    await message.delete()


@KGBot.on_message(filters.me & (filters.command('rsq')))
async def rsqoutes_handler(app, message: Message):
    args = message.command[1:]
    if '!file' in args:
        is_file = True
        args.remove('!file')
    else:
        is_file = False

    count = args and args[0].isnumeric() and int(args[0]) or 1

    reply = message.reply_to_message
    if not (args or reply):
        return await message.edit(get_string('no_args'))

    await message.edit(get_string('loading'))

    messages = []

    current_reply = await app.get_messages(message.chat.id, reply.id, replies=count)
    for _ in range(count):
        try:
            messages.append(pack_message(
                *(await parse_messages(app, message, '', current_reply))
            ))
        except Exception as e:
            return await message.edit(get_string('module_error', error=repr(e)))

        current_reply = current_reply.reply_to_message
        if not current_reply:
            break

    await message.edit(get_string('api_request'))
    payload = {'messages': messages[::-1]}
    r = await _api_request(payload)
    open("payload.json", "w", encoding='utf8').write(json.dumps(payload, indent=4, ensure_ascii=False))

    if r.status_code != 200:
        return await message.edit(get_string('api_error'))

    quote = io.BytesIO(r.content)
    quote.name = "SQuote.webp"

    await message.edit(get_string('sending'))
    if is_file:
        await app.send_document(
            message.chat.id, quote,
            force_document=True,
            reply_to_message_id=(reply or message).id
        )
    else:
        await app.send_sticker(message.chat.id, quote, reply_to_message_id=(reply or message).id)

    await message.delete()


@KGBot.on_message(filters.me & filters.command('msq'))
async def msquotes_handler(app, message: Message):
    args = message.command[1:]
    if '!file' in args:
        is_file = True
        args.remove('!file')
    else:
        is_file = False

    count = args and args[0].isnumeric() and int(args[0]) or 1

    reply = message.reply_to_message
    if not (args or reply):
        return await message.edit(get_string('no_args'))

    await message.edit(get_string('loading'))

    messages = []

    current_message = reply
    i = reply.id
    for _ in range(count):
        try:
            messages.append(pack_message(
                *(await parse_messages(app, message, '', current_message))
            ))
        except Exception as e:
            return await message.edit(get_string('module_error', error=repr(e)))

        while i > 0:
            i -= 1
            current_message = await app.get_messages(message.chat.id, i)
            if not current_message.empty:
                break
        else:
            break

    await message.edit(get_string('api_request'))
    payload = {'messages': messages[::-1]}
    r = await _api_request(payload)
    open("payload.json", "w", encoding='utf8').write(json.dumps(payload, indent=4, ensure_ascii=False))

    if r.status_code != 200:
        return await message.edit(get_string('api_error'))

    quote = io.BytesIO(r.content)
    quote.name = "SQuote.webp"

    await message.edit(get_string('sending'))
    if is_file:
        await app.send_document(
            message.chat.id,
            quote,
            force_document=True,
            reply_to_message_id=(reply or message).id
        )
    else:
        await app.send_sticker(message.chat.id, quote, reply_to_message_id=(reply or message).id)

    await message.delete()


async def parse_messages(app: KGBot, message: Message, args: str, reply: Message):
    args_ = args.split()
    text = media = user_id = name = avatar = rank = reply_id = reply_name = reply_text = entities = None

    if reply and reply.forward_date:
        user = reply.forward_from

        if user:
            user_id = user.id
            user_photo = user.photo
        elif reply.forward_from_chat:
            user_id = reply.forward_from_chat.id
            user_photo = reply.forward_from_chat.photo
        else:
            user_id = 0
            user_photo = None

        name = full_name(reply)
        text, entities = get_text(args, reply)

    elif reply:
        if not args:
            reply = await app.get_messages(reply.chat.id, reply.id)
            r = reply.reply_to_message
            if r:
                if r.from_user:
                    reply_id = r.from_user.id
                elif r.forward_from_chat:
                    reply_id = r.forward_from_chat.id
                else:
                    reply_id = r.chat.id

                reply_name = full_name(r)

                reply_text = get_reply_text(r)

        user = reply.from_user
        user_photo = (
            user.photo
            if user
            else reply.forward_from_chat.photo
            if reply.forward_from_chat
            else reply.chat.photo
        )
        user_id = user.id if user else reply.chat.id
        name = full_name(reply)
        text, entities = get_text(args, reply)

    else:
        try:
            user = await app.get_users(int(args_[0]) if args_[0].isdigit() else args_[0])
            if len(args_) < 2:
                user = await app.get_users(int(args) if args.isdigit() else args)
            else:
                text = args.split(maxsplit=1)[1]
        except (ValueError, IndexError):
            user = message.from_user
        user_photo = (
            user.photo
            if user
            else None
        )
        user_id = user.id if user else reply.chat.id

        name = user.first_name + (' ' + user.last_name if user.last_name else '')

    if user_photo:
        avatar_path = await app.download_media(user_photo.small_file_id)
        avatar = open(avatar_path, 'rb').read()
        os.remove(avatar_path)
        avatar = base64.b64encode(avatar).decode() if avatar else None

    thumb = get_thumb(reply)
    if thumb:
        media_path = await app.download_media(thumb)
        media = (open(media_path, 'rb').read())
        os.remove(media_path)
        media = base64.b64encode(media).decode()

    entities = convert_entities(entities)

    rank = ""
    if reply.chat.type in ('group', 'supergroup') and user:
        try:
            chat_member = await app.get_chat_member(reply.chat.id, user.id)
        except:
            pass
        else:
            if chat_member.status in ('creator', 'administrator'):
                rank = chat_member.chat.title or chat_member.status

    return text, media, user_id, name, avatar, rank, reply_id, reply_name, reply_text, entities


def pack_message(text, media, user_id, name, avatar, rank, reply_id, reply_name, reply_text, entities):
    return {
        "text": text,
        "media": media,
        "entities": entities or [],
        "author": {
            "id": user_id,
            "name": name,
            "avatar": avatar,
            "rank": rank
        },
        "reply": {
            "id": reply_id,
            "name": reply_name,
            "text": reply_text
        }
    }


def get_thumb(reply: Message):
    if reply and reply.media:
        if reply.photo:
            return reply.photo
        if reply.sticker:
            if not reply.sticker.is_animated:
                return reply.sticker
            elif reply.sticker.thumbs:
                return reply.sticker.thumbs[0]

        data = reply.video or reply.animation or reply.video_note or reply.audio or reply.document

        if data and data.thumbs:
            return data.thumbs[0]

        if reply.web_page:
            return reply.web_page.photo or reply.web_page.animation or reply.web_page.video


def get_text(args: str, reply: Message):
    text = args or reply.text or reply.caption or ''

    media_text = (
        "📊 Опрос"
        if reply.poll and reply.poll.type == 'regular'
        else "📊 Викторина"
        if reply.poll and reply.poll.type == 'quiz'
        else "🖼 GIF"
        if reply.animation and not reply.animation.thumbs
        else "📹 Видео"
        if reply.video and not reply.video.thumbs
        else "📹 Видеосообщение"
        if reply.video_note and not reply.video_note.thumbs
        else sticker_text(reply.sticker)
        if reply.sticker and reply.sticker.is_animated and not reply.sticker.thumbs
        else "📍 Местоположение"
        if reply.location
        else "👤 Контакт"
        if reply.contact
        else "🎧 Музыка" + get_audio_text(reply.audio)
        if reply.audio
        else "🎵 Голосовое сообщение"
        if reply.voice
        else "💾 Файл " + reply.document.file_name
        if reply.document
        else ''
    )

    simbols_to_add = 0
    if media_text and text:
        text = media_text + '\n\n' + text
        simbols_to_add = len(media_text + '\n\n')
    elif media_text:
        text = media_text
        simbols_to_add = len(media_text)

    entities = reply.entities or reply.caption_entities
    if entities and simbols_to_add:
        for i in entities:
            i.offset += simbols_to_add

    return text, entities


def get_reply_text(r: Message):
    text = (
        "📷 Фото"
        if r.photo
        else "📊 Опрос"
        if r.poll and r.poll.type == 'regular'
        else "📊 Викторина"
        if r.poll and r.poll.type == 'quiz'
        else "📍 Местоположение"
        if r.location or r.venue
        else "👤 Контакт"
        if r.contact
        else "🖼 GIF"
        if r.animation
        else "🎧 Музыка" + get_audio_text(r.audio)
        if r.audio
        else "📹 Видео"
        if r.video
        else "📹 Видеосообщение"
        if r.video_note
        else "🎵 Голосовое сообщение"
        if r.voice
        else sticker_text(r.sticker)
        if r.sticker
        else "💾 Файл " + r.document.file_name
        if r.document
        else r.text or "Unsupported message media"
    )

    return text


def get_audio_text(audio: Audio):
    if audio.title and audio.performer:
        return f' ({audio.title} — {audio.performer})'
    elif audio.title:
        return f' ({audio.title})'
    elif audio.performer:
        return f' ({audio.performer})'
    else:
        return ''


def convert_entities(entities: List[MessageEntity]):
    # coded by @droox
    if not entities:
        return

    res = []
    if entities:
        for entity in entities:
            d_entity = json.loads(str(entity).replace('\'', '"'))
            d_entity.pop("_", None)
            res.append(d_entity)
    return res


async def _api_request(data: dict):
    return requests.post(API_ENDPOINT, json=data)


def full_name(message: Message):
    if message.forward_from:
        user = message.forward_from
        name = user.first_name + (' ' + user.last_name if user.last_name else '')

    elif message.forward_sender_name:
        name = message.forward_sender_name

    elif message.from_user:
        user = message.from_user
        if user.is_deleted:
            name = get_string('deleted_account')
        else:
            name = user.first_name + (' ' + user.last_name if user.last_name else '')

    elif message.forward_from_chat:
        name = message.forward_from_chat.title + (
            ' ({})'.format(message.forward_signature)
            if message.forward_signature else '')
    else:
        name = message.chat.title + (
            ' ({})'.format(message.author_signature)
            if message.author_signature else '')

    name = name[:26] + '...' if len(name) > 25 else name + (
        " via @" + message.via_bot.username if message and message.via_bot else "")

    return name


def sticker_text(sticker: Sticker):
    if not sticker.is_animated:
        return ((sticker.emoji + ' ') if sticker.emoji else '') + "Стикер"
    else:
        return ((sticker.emoji + ' ') if sticker.emoji else '') + "Анимированный стикер"

# aids, ne tupi
