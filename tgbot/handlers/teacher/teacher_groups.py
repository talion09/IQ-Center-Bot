from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from aiogram import Dispatcher
from aiogram import types
from tgbot.keyboards.inline.catalog import teacher_clb, date_clb, present_clb


# 📝 Мои группы
async def get_types(message: types.Message):
    db = message.bot.get("db")
    teacher = await db.select_teacher(telegram_id=message.from_user.id)
    teacher_id = int(teacher.get("id"))
    all_subjects = await db.select_in_teachers(teacher_id=teacher_id)
    if all_subjects == 0:
        await message.answer("Вы не ведете никакие группы в данной момент")
    else:
        markup = InlineKeyboardMarkup(row_width=1)
        unique_types = set()
        for id, type_id, type, subject_id, subject, description, day_id, day, time_id, time, teacher_id in all_subjects:
            if type not in unique_types:
                unique_types.add(type)
                markup.insert(InlineKeyboardButton(text=type, callback_data=teacher_clb.new(action="type_id",
                                                                                            teacher_id=teacher_id,
                                                                                            type_id=type_id,
                                                                                            subject_id=0, day_id=0,
                                                                                            time_id=0)))
        await message.answer("Выберите тип курса:", reply_markup=markup)


# back1
async def back_to_types(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    teacher = await db.select_teacher(telegram_id=call.from_user.id)
    teacher_id = int(teacher.get("id"))
    all_subjects = await db.select_in_teachers(teacher_id=teacher_id)
    markup = InlineKeyboardMarkup(row_width=1)
    unique_types = set()
    for id, type_id, type, subject_id, subject, description, day_id, day, time_id, time, teacher_id in all_subjects:
        if type not in unique_types:
            unique_types.add(type)
            markup.insert(InlineKeyboardButton(text=type, callback_data=teacher_clb.new(action="type_id", teacher_id=teacher_id, type_id=type_id, subject_id=0, day_id=0, time_id=0)))
    await call.bot.edit_message_text("Выберите тип курса:", call.from_user.id, call.message.message_id, reply_markup=markup)


# type_id / back2
async def get_subjects(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    teacher_id = int(callback_data.get("teacher_id"))
    type_id = int(callback_data.get("type_id"))

    all_subjects = await db.select_in_types_teach(teacher_id=teacher_id, type_id=type_id)
    unique_subjects = set()
    markup = InlineKeyboardMarkup(row_width=1)
    for id, type_id, type, subject_id, subject, description, day_id, day, time_id, time, teacher_id in all_subjects:
        if subject not in unique_subjects:
            unique_subjects.add(subject)
            markup.insert(InlineKeyboardButton(text=subject, callback_data=teacher_clb.new(action="subject_id", teacher_id=teacher_id, type_id=type_id, subject_id=subject_id, day_id=0, time_id=0)))
    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=teacher_clb.new(action="back1", teacher_id=teacher_id, type_id=type_id, subject_id=0, day_id=0, time_id=0)))
    await call.bot.edit_message_text("Выберите предмет:", call.from_user.id, call.message.message_id, reply_markup=markup)


# subject_id / back3
async def get_days(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    teacher_id = int(callback_data.get("teacher_id"))
    type_id = int(callback_data.get("type_id"))
    subject_id = int(callback_data.get("subject_id"))

    all_subjects = await db.select_in_subjects_teach(teacher_id=teacher_id, type_id=type_id, subject_id=subject_id)
    unique_days = set()
    markup = InlineKeyboardMarkup(row_width=1)
    for id, type_id, type, subject_id, subject, description, day_id, day, time_id, time, teacher_id in all_subjects:
        if day not in unique_days:
            unique_days.add(day)
            markup.insert(InlineKeyboardButton(text=day, callback_data=teacher_clb.new(action="day_id", teacher_id=teacher_id, type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=0)))
    text = f"Выберите день:"
    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=teacher_clb.new(action="back2", teacher_id=teacher_id, type_id=type_id, subject_id=subject_id, day_id=0, time_id=0)))
    await call.bot.edit_message_text(text, call.from_user.id, call.message.message_id, reply_markup=markup)


# day_id / back4
async def get_times(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    teacher_id = int(callback_data.get("teacher_id"))
    type_id = int(callback_data.get("type_id"))
    subject_id = int(callback_data.get("subject_id"))
    day_id = int(callback_data.get("day_id"))

    all_subjects = await db.select_in_days_teach(teacher_id=teacher_id, type_id=type_id, subject_id=subject_id, day_id=day_id)
    unique_times = {}
    markup = InlineKeyboardMarkup(row_width=1)

    for id, type_id, type, subject_id, subject, description, day_id, day, time_id, time, teacher_id in all_subjects:
        if time not in unique_times:
            unique_times[time] = (type_id, subject_id, day_id, time_id)

    sorted_unique_times = sorted(unique_times.keys())

    for time in sorted_unique_times:
        type_id, subject_id, day_id, time_id = unique_times[time]
        markup.insert(InlineKeyboardButton(text=time,
                                           callback_data=teacher_clb.new(action="time_id", teacher_id=teacher_id,
                                                                         type_id=type_id, subject_id=subject_id,
                                                                         day_id=day_id, time_id=time_id)))

    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=teacher_clb.new(action="back3", teacher_id=teacher_id, type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=0)))
    await call.bot.edit_message_text("Выберите время:", call.from_user.id, call.message.message_id, reply_markup=markup)


# time_id / back5
async def get_teacher(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    teacher_id = int(callback_data.get("teacher_id"))
    type_id = int(callback_data.get("type_id"))
    subject_id = int(callback_data.get("subject_id"))
    day_id = int(callback_data.get("day_id"))
    time_id = int(callback_data.get("time_id"))

    markup = InlineKeyboardMarkup(row_width=1)
    markup.insert(InlineKeyboardButton(text="Мои ученики", callback_data=teacher_clb.new(action="my_students", teacher_id=teacher_id, type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id)))
    markup.insert(InlineKeyboardButton(text="Посещаемость", callback_data=teacher_clb.new(action="attendance", teacher_id=teacher_id, type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id)))
    markup.insert(InlineKeyboardButton(text="Оценки", callback_data=teacher_clb.new(action="marks", teacher_id=teacher_id, type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id)))
    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=teacher_clb.new(action="back4", teacher_id=teacher_id, type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id)))
    await call.bot.edit_message_text("Выберите:", call.from_user.id, call.message.message_id, reply_markup=markup)


# my_students
async def my_students(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    teacher_id = int(callback_data.get("teacher_id"))
    type_id = int(callback_data.get("type_id"))
    subject_id = int(callback_data.get("subject_id"))
    day_id = int(callback_data.get("day_id"))
    time_id = int(callback_data.get("time_id"))

    subjects = await db.select_teacher_group(teacher_id=teacher_id, type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id)
    teacher_group_id = int(subjects.get("id"))

    group = await db.select_groups(teacher_group_id=teacher_group_id)
    if len(group) == 0:
        text = f"У вас пока что нет учеников в этой группе"
    else:
        text = f"Мои ученики:\n\n"
        for index, (id, teacher_group_id, student_id) in enumerate(group, start=1):
            student = await db.select_student(id=student_id)
            user_id = student.get("telegram_id")
            user = await db.select_user(telegram_id=user_id)
            full_name = user.get("full_name")
            text += f"{index}. {full_name}\n"

    markup = InlineKeyboardMarkup(row_width=1)
    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=teacher_clb.new(action="back5", teacher_id=teacher_id, type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id)))
    await call.bot.edit_message_text(text, call.from_user.id, call.message.message_id, reply_markup=markup)


# attendance / back6
async def attendance(call: CallbackQuery, callback_data: dict):
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

    for date_string, id in lesson_datees.items():
        markup.insert(InlineKeyboardButton(text=date_string, callback_data=date_clb.new(action="lesson_date", teacher_group_id=teacher_group_id, attendance_id=id)))
    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=teacher_clb.new(action="back5", teacher_id=teacher_id, type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id)))
    await call.bot.edit_message_text("Выберите дату:", call.from_user.id, call.message.message_id, reply_markup=markup)


# lesson_date
async def lesson_date_handler(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    teacher_group_id = int(callback_data.get("teacher_group_id"))
    attendance_id = int(callback_data.get("attendance_id"))

    markup = InlineKeyboardMarkup(row_width=3)
    lesson_date = await db.select_attendance_record(id=attendance_id)
    date_obj = lesson_date.get("lesson_date")
    attendances = await db.select_attendances_2(teacher_group_id=teacher_group_id, lesson_date=date_obj)
    full_names = ""
    for id, teacher_group_id, student_id, lesson_date, attendance, marks in attendances:
        student = await db.select_student(id=student_id)
        user_id = student.get("telegram_id")
        user = await db.select_user(telegram_id=user_id)
        full_name = user.get("full_name")
        full_names += f"{full_name} \n"
        if attendance is None:
            inline_btn = InlineKeyboardButton(text=full_name, callback_data=present_clb.new(action="name", attendance_id=id, teacher_group_id=teacher_group_id))
            markup.row(inline_btn)
            markup.add(InlineKeyboardButton(text="✅", callback_data=present_clb.new(action="present", attendance_id=id, teacher_group_id=teacher_group_id)))
            markup.insert(InlineKeyboardButton(text="❌", callback_data=present_clb.new(action="not_present", attendance_id=id, teacher_group_id=teacher_group_id)))
        else:
            if str(attendance) == "False":
                markup.row(InlineKeyboardButton(text=f"❌ {full_name}", callback_data=present_clb.new(action="present_update", attendance_id=id, teacher_group_id=teacher_group_id)))
            else:
                markup.row(InlineKeyboardButton(text=f"✅ {full_name}", callback_data=present_clb.new(action="not_present_update", attendance_id=id, teacher_group_id=teacher_group_id)))

    subjects = await db.select_teacher_group(id=teacher_group_id)
    teacher_id = int(subjects.get("teacher_id"))
    type_id = int(subjects.get("type_id"))
    subject_id = int(subjects.get("subject_id"))
    day_id = int(subjects.get("day_id"))
    time_id = int(subjects.get("time_id"))
    markup.row(InlineKeyboardButton(text="⬅️ Назад", callback_data=teacher_clb.new(action="back6", teacher_id=teacher_id, type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id)))
    await call.bot.edit_message_text("Ученики:", call.from_user.id, call.message.message_id, reply_markup=markup)


# name / present / not_present
async def student_present_or_not(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    attendance_id = int(callback_data.get("attendance_id"))
    teacher_group_id = int(callback_data.get("teacher_group_id"))
    action = callback_data.get("action")

    attendance = await db.select_attendance_record(id=attendance_id)
    lesson_date = attendance.get("lesson_date")
    student_id = int(attendance.get("student_id"))
    student = await db.select_student(id=student_id)
    remaining_lessons = int(student.get("remaining_lessons"))

    if action == "name":
        pass
    elif action == "present":
        await db.update_attendance_record(id=attendance_id, attendance=True)
        await db.update_student(id=student_id, remaining_lessons=(remaining_lessons - 1))
        await lesson_date_handler(call, callback_data)
    else:
        await db.add_skip(student_id=student_id, lesson_date=lesson_date)
        await db.update_attendance_record(id=attendance_id, attendance=False)
        await db.update_student(id=student_id, remaining_lessons=(remaining_lessons - 1))
        await lesson_date_handler(call, callback_data)


# present_update / not_present_update
async def student_present_or_not_update(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    attendance_id = int(callback_data.get("attendance_id"))
    teacher_group_id = int(callback_data.get("teacher_group_id"))
    action = callback_data.get("action")

    attendance = await db.select_attendance_record(id=attendance_id)
    student_id = int(attendance.get("student_id"))
    lesson_date = attendance.get("lesson_date")

    if action == "present_update":
        await db.delete_skip(student_id=student_id, lesson_date=lesson_date)

        await db.update_attendance_record(id=attendance_id, attendance=True)
        await lesson_date_handler(call, callback_data)
    else:
        await db.add_skip(student_id=student_id, lesson_date=lesson_date)

        await db.update_attendance_record(id=attendance_id, attendance=False)
        await lesson_date_handler(call, callback_data)


def register_teacher_groups(dp: Dispatcher):
    # dp.register_message_handler(get_types, IsTeacher(), text="👥 Мои группы")
    dp.register_message_handler(get_types, text="👥 Мои группы")
    dp.register_callback_query_handler(back_to_types, teacher_clb.filter(action="back1"))

    dp.register_callback_query_handler(get_subjects, teacher_clb.filter(action="type_id"))
    dp.register_callback_query_handler(get_subjects, teacher_clb.filter(action="back2"))

    dp.register_callback_query_handler(get_days, teacher_clb.filter(action="subject_id"))
    dp.register_callback_query_handler(get_days, teacher_clb.filter(action="back3"))

    dp.register_callback_query_handler(get_times, teacher_clb.filter(action="day_id"))
    dp.register_callback_query_handler(get_times, teacher_clb.filter(action="back4"))

    dp.register_callback_query_handler(get_teacher, teacher_clb.filter(action="time_id"))
    dp.register_callback_query_handler(get_teacher, teacher_clb.filter(action="back5"))

    dp.register_callback_query_handler(my_students, teacher_clb.filter(action="my_students"))

    dp.register_callback_query_handler(attendance, teacher_clb.filter(action="attendance"))
    dp.register_callback_query_handler(attendance, teacher_clb.filter(action="back6"))

    dp.register_callback_query_handler(lesson_date_handler, date_clb.filter(action="lesson_date"))

    dp.register_callback_query_handler(student_present_or_not, present_clb.filter(action="name"))
    dp.register_callback_query_handler(student_present_or_not, present_clb.filter(action="present"))
    dp.register_callback_query_handler(student_present_or_not, present_clb.filter(action="not_present"))

    dp.register_callback_query_handler(student_present_or_not_update, present_clb.filter(action="present_update"))
    dp.register_callback_query_handler(student_present_or_not_update, present_clb.filter(action="not_present_update"))











