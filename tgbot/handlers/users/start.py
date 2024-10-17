from re import compile
import schedule
import time
import asyncio
from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart, Command
from aiogram.types import ReplyKeyboardRemove
import datetime

from aiogram.utils.deep_linking import decode_payload

from tgbot.filters.is_admin import IsAdmin
from tgbot.keyboards.default.language import lang
from tgbot.keyboards.default.main_menu import m_menu, admin_menu, student_office, teacher_office, admin_teacher_menu
from tgbot.states.users import User, Deep_link, Admins


async def suitable_menu(message):
    db = message.bot.get("db")
    admins_list = []
    teachers_list = []

    for id, telegram_id, name in await db.select_all_admins():
        admins_list.append(telegram_id)

    for id, telegram_id, description in await db.select_all_teachers():
        teachers_list.append(telegram_id)

    if message.from_user.id in admins_list:
        if message.from_user.id in teachers_list:
            menu = admin_teacher_menu
        else:
            menu = admin_menu
    else:
        menu = m_menu
    return menu


async def bot_start(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    await state.reset_state()
    try:
        user_in_db = await db.select_user(telegram_id=int(message.from_user.id))
        full_name = user_in_db.get("full_name")
        menu = await suitable_menu(message)
        await message.answer(f"<b>{full_name}</b>, выберите что вас интересует:", reply_markup=menu)
    except AttributeError:
        await message.answer(
            f"Здравствуйте! {message.from_user.full_name}\nВведите Ваше Имя и Фамилию",
            reply_markup=ReplyKeyboardRemove())
        await User.Name.set()


async def fill_attendance(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    await state.reset_state()

    while True:
        today = datetime.datetime.now()
        day_of_week = today.weekday()
        days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        today_day = days[day_of_week]
        formatted_date = today.strftime('%Y-%m-%d')

        list_teacher_group_id = await db.select_teacher_group_id(day=f"%{today_day}%")
        for teacher_group_id in list_teacher_group_id:
            group = await db.select_groups(teacher_group_id=int(teacher_group_id.get("id")))
            if len(group) == 0:
                pass
            else:
                for id, teacher_group_id, student_id in group:
                    selected = await db.select_attendance_record(teacher_group_id=teacher_group_id, student_id=student_id, lesson_date=today)
                    try:
                       selected.get("id")
                    except:
                        await db.add_attendance_record(teacher_group_id=teacher_group_id, student_id=student_id,
                                                       lesson_date=today, attendance=None, marks=None)

        # list_teacher_group_id = await db.select_teacher_group_id(day=f"%{today_day}%")
        # selected = await db.select_attendance_record(lesson_date=today)
        # try:
        #     selected.get("id")
        # except:
        #     for teacher_group_id in list_teacher_group_id:
        #         group = await db.select_groups(teacher_group_id=int(teacher_group_id.get("id")))
        #         if len(group) == 0:
        #             pass
        #         else:
        #             for id, teacher_group_id, student_id in group:
        #                 await db.add_attendance_record(teacher_group_id=teacher_group_id, student_id=student_id,
        #                                                lesson_date=today, attendance=None, marks=None)
        await message.bot.send_message(153479611, "Обновлены посещения")
        await asyncio.sleep(60*60*24)


# Deep_link.New_description
async def teacher_descrip(message: types.Message, state: FSMContext):
    data = await state.get_data()
    id = int(data.get("id"))
    db = message.bot.get("db")
    description = message.text
    await db.add_teacher(telegram_id=message.from_user.id, description=description)
    await db.update_deep_link(id=id, is_used=True)
    await state.reset_state()
    await message.answer("Вы успешно зарегестрировались в боте как учитель")


async def start_deep(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    await state.reset_state()
    try:
        args = message.get_args()
        argument = decode_payload(args)
        splitted_args = argument.split(":")
        teacher_group_id = splitted_args[0]
        id_deep_link = splitted_args[1]
        link = await db.select_deep_link(id=int(id_deep_link))
        is_used = link.get("is_used")
        if str(is_used) == "False":
            try:
                user_in_db = await db.select_user(telegram_id=int(message.from_user.id))
                full_name = user_in_db.get("full_name")
                if teacher_group_id == "teacher":
                    await message.answer(f"<b>{full_name}</b>, отправьте текст о себе и о своих навыках")
                    await Deep_link.New_description.set()
                    await state.update_data(id=int(id_deep_link))
                else:
                    today = datetime.datetime.now()
                    student = await db.select_student(telegram_id=message.from_user.id)
                    try:
                        student.get("id")
                    except:
                        student = await db.add_student(telegram_id=message.from_user.id, registration_date=today,
                                                   remaining_lessons=12)
                    student_id = int(student.get("id"))
                    await db.add_group(teacher_group_id=int(teacher_group_id), student_id=student_id)
                    await db.update_deep_link(id=int(id_deep_link), is_used=True)
                    await message.answer(f"{full_name}, вы успешно зарегестрировались в боте как ученик")
            except AttributeError:
                await message.answer(
                    f"Здравствуйте! {message.from_user.full_name}\nВведите Ваше Имя и Фамилию",
                    reply_markup=ReplyKeyboardRemove())
                await User.Name.set()
        else:
            await message.answer("Ссылка уже была использована!")
    except:
        try:
            user_in_db = await db.select_user(telegram_id=int(message.from_user.id))
            full_name = user_in_db.get("full_name")
            menu = await suitable_menu(message)
            await message.answer(f"<b>{full_name}</b>, выберите что вас интересует:", reply_markup=menu)
        except AttributeError:
            await message.answer(
                f"Здравствуйте! {message.from_user.full_name}\nВведите Ваше Имя и Фамилию",
                reply_markup=ReplyKeyboardRemove())
            await User.Name.set()


async def add_owner(message: types.Message):
    db = message.bot.get('db')
    await db.add_administrator(telegram_id=int(153479611), name="Мухаммад")


def register_start(dp: Dispatcher):
    dp.register_message_handler(start_deep, CommandStart(), state="*")
    dp.register_message_handler(start_deep, text="Отменить", state=Admins)
    dp.register_message_handler(start_deep, text="🏡 Главное меню", state="*")
    dp.register_message_handler(teacher_descrip, state=Deep_link.New_description)
    dp.register_message_handler(fill_attendance, IsAdmin(), Command("fill_attendance"), state="*")
    dp.register_message_handler(add_owner, Command("add_owner"))



