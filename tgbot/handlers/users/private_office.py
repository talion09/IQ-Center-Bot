from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart, Command
from aiogram.types import ReplyKeyboardRemove
import datetime

from tgbot.keyboards.default.language import lang
from tgbot.keyboards.default.main_menu import m_menu, admin_menu, student_office, teacher_office
from tgbot.states.users import User


async def suitable_menu(message):
    db = message.bot.get("db")
    admins_list = await db.select_id_admins()

    if message.from_user.id in admins_list:
        menu = admin_menu
    else:
        menu = m_menu
    return menu


async def suitable_office(message):
    db = message.bot.get("db")
    student_list = []
    teacher_list = []

    for id, telegram_id, registration_date, remaining_lessons in await db.select_all_students():
        student_list.append(telegram_id)

    for id, telegram_id, description in await db.select_all_teachers():
        teacher_list.append(telegram_id)

    if message.from_user.id in student_list:
        menu = student_office
    elif message.from_user.id in teacher_list:
        menu = teacher_office
    else:
        return "Null"
    return menu


async def st_office(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    await state.reset_state()
    user_in_db = await db.select_user(telegram_id=int(message.from_user.id))
    full_name = user_in_db.get("full_name")
    menu = await suitable_office(message)
    if menu == "Null":
        await message.answer(f"<b>{full_name}</b>, Вы не являетесь учеником/учителем IQ Центра")
    else:
        await message.answer(f"<b>{full_name}</b>, выберите что вас интересует:", reply_markup=menu)


async def student_officee(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    await state.reset_state()
    user_in_db = await db.select_user(telegram_id=int(message.from_user.id))
    full_name = user_in_db.get("full_name")
    await message.answer(f"<b>{full_name}</b>, выберите что вас интересует:", reply_markup=student_office)


async def teacher_officee(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    await state.reset_state()
    user_in_db = await db.select_user(telegram_id=int(message.from_user.id))
    full_name = user_in_db.get("full_name")
    await message.answer(f"<b>{full_name}</b>, выберите что вас интересует:", reply_markup=teacher_office)


def register_private_office(dp: Dispatcher):
    dp.register_message_handler(st_office, text="💼 Личный Кабинет")

    dp.register_message_handler(student_officee, text="💼 Личный Кабинет Ученика")
    dp.register_message_handler(teacher_officee, text="💼 Личный Кабинет Учителя")



