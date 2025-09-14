from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_async_session
from database.module import User, Task


async def get_user(tg_id, session:AsyncSession):
    #Функция поиска человека по id. Используеться чаще всего для подтверждения присутствия аккаунта в БД
    response = await session.execute(select(User).where(User.tg_id == tg_id))
    user = response.scalars().first()
    return user
async def send_tasks_list(user, target, state: FSMContext):
    #Вывод списка задач юзера
    async with get_async_session() as session:
        result = await session.execute(select(Task).where(Task.user_id == user.id))
        tasks_list = result.scalars().all()

    if not tasks_list:
        await target.answer("У вас пока нет задач!" if isinstance(target, types.Message) else "❌ У вас пока нет задач!", show_alert=True)
        await state.clear()
        return

    buttons = [
        [InlineKeyboardButton(text=f"{'✅' if task.completed else '❌'} {task.title}",
                              callback_data=f"task_{task.id}")]
        for task in tasks_list
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    if isinstance(target, types.Message):
        await target.answer(f"Все задачи пользователя {user.name}:", reply_markup=keyboard)
    else:
        await target.message.edit_text(f"Все задачи пользователя {user.name}:", reply_markup=keyboard)

    await state.clear()
async def show_task_menu(message: types.Message, task_id: int, state: FSMContext):
    #Опции задачи
    await state.update_data(selected_task_id=task_id)

    async with get_async_session() as session:
        task = await session.get(Task, task_id)
        if not task:
            await message.answer("Задача не найдена")
            return
        status_btn_text = "✅ Отметить невыполненной" if task.completed else "❌ Отметить выполненной"

    buttons = [
        [InlineKeyboardButton(text=status_btn_text, callback_data="toggle_task_status")],
        [InlineKeyboardButton(text="🗑 Удалить", callback_data="delete_task")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_tasks")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.edit_text("Что сделать с этой задачей?", reply_markup=keyboard)

