import inspect
import logging

import pyrogram
from pyrogram.client import Dispatcher
from pyrogram.errors import ChatIdInvalid, PeerIdInvalid
from pyrogram.handlers import RawUpdateHandler

log = logging.getLogger(__name__)


class CustomDispatcher(Dispatcher):
    async def handler_worker(self, lock):
        while True:
            packet = await self.updates_queue.get()

            if packet is None:
                break

            try:
                update, users, chats = packet
                parser = self.update_parsers.get(type(update), None)

                parsed_update, handler_type = (
                    await parser(update, users, chats)
                    if parser is not None
                    else (None, type(None))
                )

                async with lock:
                    for group in self.groups.values():
                        for handler in group:
                            args = None

                            if isinstance(handler, handler_type):
                                try:
                                    if await handler.check(self.client, parsed_update):
                                        args = (parsed_update,)
                                except Exception as e:
                                    log.exception(e)
                                    continue

                            elif isinstance(handler, RawUpdateHandler):
                                args = (update, users, chats)

                            if args is None:
                                continue

                            try:
                                if inspect.iscoroutinefunction(handler.callback):
                                    # noinspection PyUnresolvedReferences
                                    logger = logging.getLogger(mod_name := handler.callback.__module__)
                                    await handler.callback(self.client, *args)
                                else:
                                    await self.loop.run_in_executor(
                                        self.client.executor,
                                        handler.callback,
                                        self.client,
                                        *args
                                    )
                            except pyrogram.StopPropagation:
                                raise
                            except pyrogram.ContinuePropagation:
                                continue
                            except Exception as error:
                                chat_id, _ = list(chats.items())[0] if chats else ('me', ...)
                                message_info = {
                                    'chat_id': chat_id,
                                    'message_id': update.message.id,
                                    'text': f'<b><i>В модуле <u>{mod_name.split(".")[1]}</u> произошла ошибка!'
                                            f'\nЧтобы узнать подробности, напишите <u>.logs 40</u></i></b>'
                                }
                                if self.client.logs_type == 'show':
                                    message_info['text'] = f'Ошибка: {str(error)}'

                                try:
                                    await self.client.edit_message_text(**message_info)
                                except PeerIdInvalid:  # либо там -100, либо там просто -
                                    message_info['chat_id'] = message_info['chat_id'] * -1
                                    try:
                                        await self.client.edit_message_text(**message_info)
                                    except ChatIdInvalid:
                                        message_info['chat_id'] = ('-100' + str(abs(message_info['chat_id'])))
                                        await self.client.edit_message_text(**message_info)

                                logger.error(msg=error, exc_info=True)

                            break
            except pyrogram.StopPropagation:
                pass
            except Exception as e:
                log.exception(e)
