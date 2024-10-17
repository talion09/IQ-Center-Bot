from aiogram import Dispatcher
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.handlers.admins.functions import get_teacher, get_times, get_days, get_subjects, get_types
from tgbot.keyboards.inline.catalog import delete_student_clb, get_students_clb, student_custom_clb, add_student_clb, \
    admins_clb, debstors_clb


# delete / back1
async def debstors_types(call: CallbackQuery, callback_data: dict):
    await get_types(call, callback_data, debstors_clb, admins_clb)


# type_id / back2
async def debstors_subjects(call: CallbackQuery, callback_data: dict):
    await get_subjects(call, callback_data, debstors_clb)


# subject_id / back3
async def debstors_days(call: CallbackQuery, callback_data: dict):
    await get_days(call, callback_data, debstors_clb)


# day_id / back4
async def debstors_students(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    type_id = int(callback_data.get("type_id"))
    subject_id = int(callback_data.get("subject_id"))
    day_id = int(callback_data.get("day_id"))

    all_subjects = await db.select_in_days(type_id=type_id, subject_id=subject_id, day_id=day_id)
    teacher_group_ids = []
    for id, type_id, type, subject_id, subject, description, day_id, day, time_id, time, teacher_id in all_subjects:
        if time not in teacher_group_ids:
            teacher_group_ids.append(id)

    text = f"Должники на сегодня:"
    markup = InlineKeyboardMarkup(row_width=1)
    for teacher_group_id in teacher_group_ids:
        groups = await db.select_groups(teacher_group_id=teacher_group_id)

        subjects = await db.select_teacher_group(id=teacher_group_id)
        time = subjects.get("time")
        teacher_id = int(subjects.get("teacher_id"))
        teacher = await db.select_teacher(id=teacher_id)
        telegram_id = int(teacher.get("telegram_id"))
        teacher_user = await db.select_user(telegram_id=telegram_id)
        teacher_full_name = teacher_user.get("full_name")
        for id, teacher_group_id, student_id in groups:
            student = await db.select_student(id=student_id)
            remaining_lessons = int(student.get("remaining_lessons"))

            if remaining_lessons <= 0:
                telegram_id = int(student.get("telegram_id"))
                user = await db.select_user(telegram_id=telegram_id)
                full_name = user.get("full_name")
                markup.insert(InlineKeyboardButton(text=f"{full_name} - {time} - {teacher_full_name}",
                                                   callback_data=get_students_clb.new(action="get_student_data",
                                                                                      teacher_group_id=teacher_group_id,
                                                                                      student_id=student_id)))
    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=debstors_clb.new(action="back3", type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=0, teacher_id=0)))
    markup.insert(InlineKeyboardButton(text="Оповестить должников?", callback_data=debstors_clb.new(action="call", type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=0, teacher_id=0)))
    await call.bot.edit_message_text(text, call.from_user.id, call.message.message_id, reply_markup=markup)


# call
async def call_debtors(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    type_id = int(callback_data.get("type_id"))
    subject_id = int(callback_data.get("subject_id"))
    day_id = int(callback_data.get("day_id"))

    text = f"Вы уверены, что хотите оповестить должников?"
    markup = InlineKeyboardMarkup(row_width=1)
    markup.insert(InlineKeyboardButton(text="Да", callback_data=debstors_clb.new(action="call_yes", type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=0, teacher_id=0)))
    markup.insert(InlineKeyboardButton(text="Нет", callback_data=debstors_clb.new(action="call_no", type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=0, teacher_id=0)))
    await call.bot.edit_message_text(text, call.from_user.id, call.message.message_id, reply_markup=markup)


# call_yes
async def call_debtors_confirm(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    type_id = int(callback_data.get("type_id"))
    subject_id = int(callback_data.get("subject_id"))
    day_id = int(callback_data.get("day_id"))

    text = f"Должники оповещены"
    await call.bot.edit_message_text(text, call.from_user.id, call.message.message_id)

    all_subjects = await db.select_in_days(type_id=type_id, subject_id=subject_id, day_id=day_id)
    teacher_group_ids = []
    for id, type_id, type, subject_id, subject, description, day_id, day, time_id, time, teacher_id in all_subjects:
        if time not in teacher_group_ids:
            teacher_group_ids.append(id)

    for teacher_group_id in teacher_group_ids:
        groups = await db.select_groups(teacher_group_id=teacher_group_id)

        subjects = await db.select_teacher_group(id=teacher_group_id)
        time = subjects.get("time")
        day = subjects.get("day")
        subject = subjects.get("subject")
        teacher_id = int(subjects.get("teacher_id"))
        teacher = await db.select_teacher(id=teacher_id)
        telegram_id = int(teacher.get("telegram_id"))
        teacher_user = await db.select_user(telegram_id=telegram_id)
        teacher_full_name = teacher_user.get("full_name")
        for id, teacher_group_id, student_id in groups:
            student = await db.select_student(id=student_id)
            remaining_lessons = int(student.get("remaining_lessons"))

            if remaining_lessons <= 0:
                telegram_id = int(student.get("telegram_id"))
                user = await db.select_user(telegram_id=telegram_id)
                full_name = user.get("full_name")
                text = f"{full_name}, у Вас задолжность в группе по <b>'{subject}'</b> в <b>'{day}'</b> в <b>'{time}'</b> у <b>'{teacher_full_name}'</b> ({remaining_lessons} урок(а)(ов))"
                await call.bot.send_message(telegram_id, text)


def register_debtors(dp: Dispatcher):
    #                                               IS_ADMIN_
    dp.register_callback_query_handler(debstors_types, admins_clb.filter(action="debstors"))
    dp.register_callback_query_handler(debstors_types, debstors_clb.filter(action="back1"))

    dp.register_callback_query_handler(debstors_subjects, debstors_clb.filter(action="type_id"))
    dp.register_callback_query_handler(debstors_subjects, debstors_clb.filter(action="back2"))

    dp.register_callback_query_handler(debstors_days, debstors_clb.filter(action="subject_id"))
    dp.register_callback_query_handler(debstors_days, debstors_clb.filter(action="back3"))

    dp.register_callback_query_handler(debstors_students, debstors_clb.filter(action="day_id"))
    dp.register_callback_query_handler(debstors_students, debstors_clb.filter(action="call_no"))

    dp.register_callback_query_handler(call_debtors, debstors_clb.filter(action="call"))

    dp.register_callback_query_handler(call_debtors_confirm, debstors_clb.filter(action="call_yes"))










