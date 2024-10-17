from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from aiogram import Dispatcher
from aiogram import types
from tgbot.keyboards.inline.catalog import teacher_clb, date_clb, present_clb, marks_clb


# marks / back6_mark
async def marks_handler(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    teacher_id = int(callback_data.get("teacher_id"))
    type_id = int(callback_data.get("type_id"))
    subject_id = int(callback_data.get("subject_id"))
    day_id = int(callback_data.get("day_id"))
    time_id = int(callback_data.get("time_id"))

    subjects = await db.select_teacher_group(teacher_id=teacher_id, type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id)
    teacher_group_id = int(subjects.get("id"))

    markup = InlineKeyboardMarkup(row_width=1)
    dates = await db.select_attendances(teacher_group_id=teacher_group_id)
    lesson_datees = {}

    for id, teacher_group_id, student_id, lesson_date, attendance, marks in dates:
        date_string = lesson_date.strftime('%Y-%m-%d')
        if date_string not in lesson_datees:
            lesson_datees[date_string] = id
        if len(lesson_datees) == 7:
            break

    for date_string, id in lesson_datees.items():
        markup.insert(InlineKeyboardButton(text=date_string, callback_data=date_clb.new(action="lesson_mark", teacher_group_id=teacher_group_id, attendance_id=id)))
    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=teacher_clb.new(action="back5", teacher_id=teacher_id, type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id)))
    await call.bot.edit_message_text("Выберите дату:", call.from_user.id, call.message.message_id, reply_markup=markup)


# lesson_mark / back7_mark
async def lesson_mark_handler(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    teacher_group_id = int(callback_data.get("teacher_group_id"))
    attendance_id = int(callback_data.get("attendance_id"))

    markup = InlineKeyboardMarkup(row_width=1)
    lesson_date = await db.select_attendance_record(id=attendance_id)
    date_obj = lesson_date.get("lesson_date")
    attendances = await db.select_attendances_2(teacher_group_id=teacher_group_id, lesson_date=date_obj)
    for id, teacher_group_id, student_id, lesson_date, attendance, marks in attendances:
        student = await db.select_student(id=student_id)
        user_id = student.get("telegram_id")
        user = await db.select_user(telegram_id=user_id)
        full_name = user.get("full_name")
        if marks is None:
            markup.insert(InlineKeyboardButton(text=full_name,
                                               callback_data=marks_clb.new(action="name", attendance_id=id,
                                                                           teacher_group_id=teacher_group_id, mark=0)))
        else:
            markup.insert(InlineKeyboardButton(text=f"{full_name} - {marks}",
                                               callback_data=marks_clb.new(action="name", attendance_id=id,
                                                                           teacher_group_id=teacher_group_id, mark=0)))

    subjects = await db.select_teacher_group(id=teacher_group_id)
    teacher_id = int(subjects.get("teacher_id"))
    type_id = int(subjects.get("type_id"))
    subject_id = int(subjects.get("subject_id"))
    day_id = int(subjects.get("day_id"))
    time_id = int(subjects.get("time_id"))
    markup.row(InlineKeyboardButton(text="⬅️ Назад", callback_data=teacher_clb.new(action="back6_mark", teacher_id=teacher_id, type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id)))
    await call.bot.edit_message_text("Ученики:", call.from_user.id, call.message.message_id, reply_markup=markup)


# name
async def student_lesson_mark(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    attendance_id = int(callback_data.get("attendance_id"))
    teacher_group_id = int(callback_data.get("teacher_group_id"))

    markup = InlineKeyboardMarkup(row_width=5)
    for mark in range(1, 6):
        markup.insert(InlineKeyboardButton(text=f"{mark}", callback_data=marks_clb.new(action="mark", attendance_id=attendance_id,
                                                                                       teacher_group_id=teacher_group_id,
                                                                                       mark=mark)))
    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=marks_clb.new(action="back7_mark", attendance_id=attendance_id, teacher_group_id=teacher_group_id, mark=0)))
    await call.bot.edit_message_text("Какую оценку поставить этому ученику?", call.from_user.id, call.message.message_id, reply_markup=markup)


# mark
async def student_mark(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    attendance_id = int(callback_data.get("attendance_id"))
    teacher_group_id = int(callback_data.get("teacher_group_id"))
    mark = int(callback_data.get("mark"))

    await db.update_attendance_record(id=attendance_id, marks=mark)
    await lesson_mark_handler(call, callback_data)

    attendance = await db.select_attendance_record(id=attendance_id)
    lesson_date = attendance.get("lesson_date")
    student_id = int(attendance.get("student_id"))
    student = await db.select_student(id=student_id)
    student_telegram_id = int(student.get("telegram_id"))
    subjects = await db.select_teacher_group(id=teacher_group_id)
    subject = subjects.get("subject")
    text = f"Вам поставили оценку за <b>'{lesson_date}'</b> по <b>'{subject}'</b> - {mark}"
    await call.bot.send_message(student_telegram_id, text)


def register_marks(dp: Dispatcher):
    dp.register_callback_query_handler(marks_handler, teacher_clb.filter(action="marks"))
    dp.register_callback_query_handler(marks_handler, teacher_clb.filter(action="back6_mark"))

    dp.register_callback_query_handler(lesson_mark_handler, date_clb.filter(action="lesson_mark"))
    dp.register_callback_query_handler(lesson_mark_handler, marks_clb.filter(action="back7_mark"))

    dp.register_callback_query_handler(student_lesson_mark, marks_clb.filter(action="name"))

    dp.register_callback_query_handler(student_mark, marks_clb.filter(action="mark"))

