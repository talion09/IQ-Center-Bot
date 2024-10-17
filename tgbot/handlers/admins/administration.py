from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.filters.is_admin import IsAdmin
from tgbot.keyboards.inline.catalog import admins_clb, student_confirm, student_lessons_confirm
from tgbot.states.users import Admins
import datetime


# Администрация
async def admins_menu(message: types.Message, state: FSMContext):
    db = message.bot.get("db")

    markup = InlineKeyboardMarkup(row_width=1)
    markup.insert(InlineKeyboardButton(text="Учителя", callback_data=admins_clb.new(action="teachers")))
    markup.insert(InlineKeyboardButton(text="Группы", callback_data=admins_clb.new(action="groups")))
    markup.insert(InlineKeyboardButton(text="Студенты", callback_data=admins_clb.new(action="students")))
    markup.insert(InlineKeyboardButton(text="Должники", callback_data=admins_clb.new(action="debstors")))
    count = await db.count_students()
    text = f"Выберите то, что Вас интересует\n\nКоличество студентов: {count}"
    await message.answer(text, reply_markup=markup)


# Администрация
async def admins_menu_clb_handler(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()

    markup = InlineKeyboardMarkup(row_width=1)
    markup.insert(InlineKeyboardButton(text="Учителя", callback_data=admins_clb.new(action="teachers")))
    markup.insert(InlineKeyboardButton(text="Группы", callback_data=admins_clb.new(action="groups")))
    markup.insert(InlineKeyboardButton(text="Студенты", callback_data=admins_clb.new(action="students")))
    markup.insert(InlineKeyboardButton(text="Должники", callback_data=admins_clb.new(action="debstors")))
    count = await db.count_students()
    text = f"Выберите то, что Вас интересует\n\nКоличество студентов: {count}"
    await call.bot.edit_message_text(text, call.from_user.id, call.message.message_id, reply_markup=markup)


async def not_confirmation_student(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    telegram_id = int(callback_data.get("telegram_id"))
    teacher_group_id = int(callback_data.get("teacher_group_id"))

    await call.bot.send_message(telegram_id, f"Вы не являетесь учеником в IQ Center")
    await call.bot.edit_message_text(call.message.text, -1002245940752, call.message.message_id)


async def confirmation_student(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    telegram_id = int(callback_data.get("telegram_id"))
    teacher_group_id = int(callback_data.get("teacher_group_id"))

    markup = InlineKeyboardMarkup(row_width=3)
    markup.insert(InlineKeyboardButton(text="< 12",
                                       callback_data=student_lessons_confirm.new(action="<",
                                                                                 student_id=telegram_id,
                                                                                 remaining_lessons=0,
                                                                                 teacher_group_id=teacher_group_id)))
    markup.insert(InlineKeyboardButton(text="12",
                                       callback_data=student_lessons_confirm.new(action=".",
                                                                                 student_id=telegram_id,
                                                                                 remaining_lessons=0,
                                                                                 teacher_group_id=teacher_group_id)))
    markup.insert(InlineKeyboardButton(text="> 12",
                                       callback_data=student_lessons_confirm.new(action=">",
                                                                                 student_id=telegram_id,
                                                                                 remaining_lessons=0,
                                                                                 teacher_group_id=teacher_group_id)))
    text = f"{call.message.text}\n\nСколько уроков осталось у этого ученика?"
    await call.bot.edit_message_text(text, -1002245940752, call.message.message_id, reply_markup=markup)


async def less_or_more(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    telegram_id = int(callback_data.get("student_id"))
    remaining_lessons = int(callback_data.get("remaining_lessons"))
    teacher_group_id = int(callback_data.get("teacher_group_id"))
    action = callback_data.get("action")

    markup = InlineKeyboardMarkup(row_width=4)
    if action == "<":
        for lesson in range(-12, 0):
            markup.insert(InlineKeyboardButton(text=str(lesson), callback_data=student_lessons_confirm.new(
                action="lessons", student_id=telegram_id, remaining_lessons=int(lesson),
                teacher_group_id=teacher_group_id)))
    elif action == ".":
        for lesson in range(1, 13):
            markup.insert(InlineKeyboardButton(text=str(lesson), callback_data=student_lessons_confirm.new(
                action="lessons", student_id=telegram_id, remaining_lessons=int(lesson),
                teacher_group_id=teacher_group_id)))
    elif action == ">":
        for lesson in range(12, 25):
            markup.insert(InlineKeyboardButton(text=str(lesson), callback_data=student_lessons_confirm.new(
                action="lessons", student_id=telegram_id, remaining_lessons=int(lesson),
                teacher_group_id=teacher_group_id)))
    else:
        pass
    await call.bot.edit_message_text(call.message.text, -1002245940752, call.message.message_id, reply_markup=markup)


async def lessons_confirmation_student(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    telegram_id = int(callback_data.get("student_id"))
    remaining_lessons = int(callback_data.get("remaining_lessons"))
    teacher_group_id = int(callback_data.get("teacher_group_id"))

    today = datetime.datetime.now()
    student = await db.select_student(telegram_id=telegram_id)
    try:
        student.get("id")
    except:
        student = await db.add_student(telegram_id=telegram_id, registration_date=today,
                                       remaining_lessons=remaining_lessons)
    student_id = int(student.get("id"))
    await db.add_group(teacher_group_id=int(teacher_group_id), student_id=student_id)
    await call.bot.send_message(telegram_id, f"Вы успешно зарегестрировались в боте как ученик")
    text = f"{call.message.text}\n\nОбработан: {remaining_lessons} уроков."
    await call.bot.edit_message_text(text, -1002245940752, call.message.message_id)


async def confirmation_student_12(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    telegram_id = int(callback_data.get("telegram_id"))
    teacher_group_id = int(callback_data.get("teacher_group_id"))

    today = datetime.datetime.now()
    student = await db.select_student(telegram_id=telegram_id)
    remaining_lessons = 12
    try:
        student.get("id")
    except:
        student = await db.add_student(telegram_id=telegram_id, registration_date=today,
                                       remaining_lessons=remaining_lessons)
    student_id = int(student.get("id"))
    await db.add_group(teacher_group_id=int(teacher_group_id), student_id=student_id)
    await call.bot.send_message(telegram_id, f"Вы успешно зарегестрировались в боте как ученик")
    text = f"{call.message.text}\n\nОбработан: {remaining_lessons} уроков."
    await call.bot.edit_message_text(text, -1002245940752, call.message.message_id)


def register_administration(dp: Dispatcher):
    #                                               IS_ADMIN_
    dp.register_message_handler(admins_menu, IsAdmin(), text="Администрация")
    dp.register_callback_query_handler(admins_menu_clb_handler, admins_clb.filter(action="back"))
    dp.register_message_handler(admins_menu, state=[Admins.New_description, Admins.New_group, Admins.Add_group], text="Отменить")

    dp.register_callback_query_handler(not_confirmation_student, student_confirm.filter(action="not"), IsAdmin())
    dp.register_callback_query_handler(confirmation_student, student_confirm.filter(action="yes"), IsAdmin())

    dp.register_callback_query_handler(less_or_more, student_lessons_confirm.filter(action="<"), IsAdmin())
    dp.register_callback_query_handler(less_or_more, student_lessons_confirm.filter(action="."), IsAdmin())
    dp.register_callback_query_handler(less_or_more, student_lessons_confirm.filter(action=">"), IsAdmin())

    dp.register_callback_query_handler(lessons_confirmation_student, student_lessons_confirm.filter(action="lessons"), IsAdmin())

    dp.register_callback_query_handler(confirmation_student_12, student_confirm.filter(action="yes_12"), IsAdmin())


