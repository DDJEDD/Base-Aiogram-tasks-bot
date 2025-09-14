from aiogram import Router, types, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from sqlalchemy import select, delete
from .func import get_user, send_tasks_list, show_task_menu
from database.db import get_async_session
from database.module import Task

tasks = Router()

class TaskStates(StatesGroup):
    waiting_for_task_name = State()

@tasks.callback_query(F.data.startswith("task_"))
#Получение таски из Callback и отображение меню с выбором действия
async def task_menu_callback(callback: CallbackQuery, state: FSMContext):
    try:
        task_id = int(callback.data.split("_")[1])
    except (IndexError, ValueError):
        await callback.answer("Некорректные данные задачи", show_alert=True)
        return
    await show_task_menu(callback.message, task_id, state)


@tasks.callback_query(F.data == "back_to_tasks")
#Возврат к списку задач
async def back_to_tasks(callback: CallbackQuery, state: FSMContext):

    async with get_async_session() as session:
        user = await get_user(callback.from_user.id, session)
    if not user:
        await callback.answer("Сначала нужно зарегистрироваться через /start", show_alert=True)
        await state.clear()
        return

    await send_tasks_list(user, callback, state)

@tasks.callback_query(F.data == "delete_task")
#Удаление задачи
async def delete_task(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    task_id = data.get("selected_task_id")

    async with get_async_session() as session:
        user = await get_user(callback.from_user.id, session)
        task = await session.get(Task, task_id)
        if task:
            stmt = delete(Task).where(Task.id == task_id)
            await session.execute(stmt)
            await session.commit()
            await callback.answer(f"Задача удалена", show_alert=False)
        else:
            await callback.answer("Задача не найдена", show_alert=True)
            return

    await send_tasks_list(user, callback, state)


@tasks.callback_query(F.data == "toggle_task_status")
#Изменение статуса задачи
async def toggle_task_status(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    task_id = data.get("selected_task_id")

    async with get_async_session() as session:
        task = await session.get(Task, task_id)
        if task:
            task.completed = not task.completed
            await session.commit()
            status = "выполненной ✅" if task.completed else "невыполненной ❌"
            await callback.answer(f"Задача теперь {status}", show_alert=False)
        else:
            await callback.answer("Задача не найдена", show_alert=True)
            return


    await show_task_menu(callback.message, task_id, state)



@tasks.message(lambda message: message.text == "добавить задачу")
#Добавление задачи
async def add_task(message: types.Message, state: FSMContext):

    await message.answer("Напиши название задачи:")
    await state.set_state(TaskStates.waiting_for_task_name)



@tasks.message(TaskStates.waiting_for_task_name)
#Получение названия задачи
async def handle_task_name(message: types.Message, state: FSMContext):
    async with get_async_session() as session:
        user = await get_user(message.from_user.id, session)
        if not user:
            await message.answer("Сначала нужно зарегистрироваться через /start")
            await state.clear()
            return

        task_name = message.text
        task = Task(title=task_name, user_id=user.id, completed=False)
        session.add(task)
        await session.commit()

        await message.answer(f"Задача '{task_name}' добавлена!")
        await state.clear()

        # Сразу показываем список всех задач
        await send_tasks_list(user, message, state)



@tasks.message(lambda message: message.text == "Все задачи")
#Показ списка всех задач
async def show_tasks(message: types.Message, state: FSMContext):

    async with get_async_session() as session:
        user = await get_user(message.from_user.id, session)

    if not user:
        await message.answer("Сначала нужно зарегистрироваться через /start")
        await state.clear()
        return

    await send_tasks_list(user, message, state)
