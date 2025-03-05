import importlib
import logging
import os
from asyncio import Task

from pyrogram import Client
from pyrogram.errors import BadRequest, SessionPasswordNeeded
from pyrogram.types import User, TermsOfService
from pyrogram.utils import ainput

from core.dispatcher import CustomDispatcher
from utils.env import Env


log = logging.getLogger(__name__)


class KGBot(Client):
    prefix = Env.get('prefix', '.')
    logs_type = 'file'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dispatcher = CustomDispatcher(self)
        print('KGBot2.0 успешно запущен')

    async def authorize(self) -> User:
        if self.bot_token:
            return await self.sign_in_bot(self.bot_token)

        print(f'Добро пожаловать в KGBot2.0')

        while True:
            try:
                if not self.phone_number:
                    while True:
                        value = await ainput("Введите номер телефона: ")

                        if not value:
                            continue

                        confirm = (await ainput(f'"{value}" верно? (д/н): ')).lower()

                        if confirm == "д":
                            break

                    if ":" in value:
                        self.bot_token = value
                        return await self.sign_in_bot(value)
                    else:
                        self.phone_number = value

                sent_code = await self.send_code(self.phone_number)
            except BadRequest as e:
                print(e.MESSAGE)
                self.phone_number = None
                self.bot_token = None
            else:
                break

        print(f"Вам был отправлен код подтверждения")

        while True:
            if not self.phone_code:
                self.phone_code = await ainput("Введите код подтверждения: ")

            try:
                signed_in = await self.sign_in(self.phone_number, sent_code.phone_code_hash, self.phone_code)
            except BadRequest as e:
                print(e.MESSAGE)
                self.phone_code = None
            except SessionPasswordNeeded as e:
                print('Двухфакторная авторизация - требуется пароль')

                while True:
                    if not self.password:
                        self.password = await ainput("Введите пароль (оставьте пустым для восстановления): ",
                                                     hide=self.hide_password)

                    try:
                        if not self.password:
                            confirm = await ainput("Подтвердите сброс пароля (д/н): ")

                            if confirm == "д":
                                email_pattern = await self.send_recovery_code()
                                print(f"Код восстановления отправлен на {email_pattern}")

                                while True:
                                    recovery_code = await ainput("Код восстановления: ")

                                    try:
                                        return await self.recover_password(recovery_code)
                                    except BadRequest as e:
                                        print(e.MESSAGE)
                                    except Exception as e:
                                        log.exception(e)
                                        raise
                            else:
                                self.password = None
                        else:
                            return await self.check_password(self.password)
                    except BadRequest as e:
                        print(e.MESSAGE)
                        self.password = None
            else:
                break

        if isinstance(signed_in, User):
            return signed_in

        while True:
            first_name = await ainput("Введите имя: ")
            last_name = await ainput("Введите фамилию (оставьте пустой, чтобы пропустить): ")

            try:
                signed_up = await self.sign_up(
                    self.phone_number,
                    sent_code.phone_code_hash,
                    first_name,
                    last_name
                )
            except BadRequest as e:
                print(e.MESSAGE)
            else:
                break

        if isinstance(signed_in, TermsOfService):
            print("\n" + signed_in.text + "\n")
            await self.accept_terms_of_service(signed_in.id)

        return signed_up

    async def get_full_name(self):
        name = self.me.first_name
        surname = self.me.last_name
        return name + ' ' + surname if surname else name


    async def modules_restart(self):
        for item in self.dispatcher.handler_worker_tasks:
            item.cancel()

        modules_to_reload = []
        for root, _, files in os.walk('plugins/'):
            for file in files:
                if file.endswith('.py') and file != '__init__.py':
                    relative_dir = os.path.relpath(root, 'plugins/')
                    module_name = os.path.splitext(file)[0]
                    
                    if relative_dir == '.':
                        full_module_name = f"plugins.{module_name}"
                    else:
                        full_module_name = f"plugins.{relative_dir.replace(os.sep, '.')}." + module_name
                    
                    modules_to_reload.append(full_module_name)

        for full_module_name in modules_to_reload:
            module = importlib.import_module(full_module_name)
            
            handlers = [obj for obj in module.__dict__.values() if hasattr(obj, 'handlers')]
            for handler in handlers:
                if handler.handlers:
                    _handler, group = handler.handlers[0]
                    if _handler in self.dispatcher.groups[0]:
                        self.remove_handler(_handler, group)

            importlib.reload(module)

            handlers = [obj for obj in module.__dict__.values() if hasattr(obj, 'handlers')]
            for handler in handlers:
                if handler.handlers:
                    _handler, group = handler.handlers[0]
                    self.add_handler(_handler, group)
                

    async def get_start_message(self):
        return f'Информация об аккаунте: \n' \
               f'Полное имя: {await self.get_full_name()}\n' \
               f'Айди: {self.me.id}\n\n'

    def check_restart(self):
        ...
