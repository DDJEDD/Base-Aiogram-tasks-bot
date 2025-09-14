from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_async_session
from database.module import User
from .func import get_user
menu = Router()
@menu.message(Command("start"))
#Проверка, иницилизация юзера в БД. Вывод меню.
async def start(message: types.Message  ):
    async with get_async_session() as session:
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        check_reg_login = await get_user(user_id, session)

        if check_reg_login:
            print("продолжаем работу, юзер зарегестрирован")
        else:
            user = User(tg_id=user_id, name=user_name)
            session.add(user)
            await session.commit()
            print("создаем юзера")
        button_today = KeyboardButton(text="добавить задачу", callback_data="add_task")
        button_tasks = KeyboardButton(text="Все задачи", callback_data="all_tasks")

        # создаем клавиатуру
        menu_kb = ReplyKeyboardMarkup(
            keyboard=[[button_today, button_tasks]],
            resize_keyboard=True
        )

        # отправляем сообщение с клавиатурой
        await message.answer(
            "Приветствую в этом планнер боте! Выберите пункт:",
            reply_markup=menu_kb
        )